from __future__ import annotations

import random
from typing import List, Tuple, TYPE_CHECKING, Optional
import color
import numpy as np
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction, BumpAction, RangedAction

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):
    entity: Actor

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y:int)->List[Tuple[int,int]]:
        """
        Compute anr return a path to the target position,
        if there is no valid path return an empty list
        """
        # copy walkable tile array
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            #check that an entity blocks movement and cost isnt zero (blocking)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # add to the cost of blocked position
                # a lower number means more enemies will crowd behind each other in
                # hallways. A higher number means enemies will take
                # longer paths in order ot surround the player
                cost[entity.x, entity.y] += 10

        # create a graph frm the cost array and pass that to a new pathfinder
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y)) #start position

        #compute the path to the desitnation and remove the starting point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        return [(index[0], index[1]) for index in path]

"""
this and any temp player stat mods work here to keep track of the number of 
turns remaining until stat modifier wears off 
"""
class DefenseModifier(BaseAI):
    def  __init__(
            self,
            entity: Actor,
            previous_ai: Optional[BaseAI],
            turns_remaining: int,
            amount: int
    ):
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining
        self.amount = amount

    def perform(self) -> None:
        if self.turns_remaining == 0:
            self.engine.message_log.add_message(
                f"Your defense returns to normal.",
                color.status_effect_applied
            )
            self.entity.fighter.base_defense -= self.amount
            self.entity.ai = self.previous_ai
        else:
            self.turns_remaining -= 1

class PowerModifier(DefenseModifier):
    def perform(self) -> None:
        if self.turns_remaining == 0:
            self.engine.message_log.add_message(
                f"Your power returns to normal.",
                color.status_effect_applied
            )
            self.entity.fighter.base_power -= self.amount
            self.entity.ai = self.previous_ai
        else:
            self.turns_remaining -= 1

class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy)) #chebyshev distance. I don't really know

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x-self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()

class RangedEnemy(HostileEnemy):
    def __init__(self, entity: Actor, range: int = 4):
        super().__init__(entity)
        self.range = range
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # chebyshev distance. I don't really know

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= self.range:
                return RangedAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()

class ConfusedEnemy(BaseAI):
    """confused enemy will stumble aimlessly for a given number
    of turns. if an actor occupies a tile it is moving into, it attacks"""
    def __init__(
            self,
            entity: Actor,
            previous_ai: Optional[BaseAI],
            turns_remaining: int,
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # revert back to original state if effect is done
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused"
            )
            self.entity.ai = self.previous_ai
        else:
            #pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1,), #NW
                    (0, -1,), #N
                    (1, -1), #NE
                    (-1, 0), #W
                    (1, 0), #E
                    (-1, 1), #SW
                    (0, 1), #S
                    (1, 1), #SE
                ]
            )
            self.turns_remaining -=1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y, ).perform()

class TimeStopAI(BaseAI):
    def __init__(
            self,
            entity: Actor,
            previous_ai: Optional[BaseAI],
            turns_remaining: int,
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # revert back to original state if effect is done
        if self.turns_remaining == 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer frozen in time"
            )
            self.entity.ai = self.previous_ai
        else:
            self.turns_remaining -= 1