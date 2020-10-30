from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    SingleRangedAttackHandler,
    AreaRangedAttackHandler,
    ActionOrHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item

class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """try to return the action for this item"""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """invoke this items ability"""
        raise NotImplementedError()

    def consume(self)->None:
        """Remove the consumed item from its containing inventory"""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)

class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The eyes of {target.name} look vacant as it starts to stumble in confusion!",
            color.status_effect_applied
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        self.consume()

class BeamConsumable(Consumable):
    def __init__(self, damage: int):
        self.damage = damage

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot shoot yourself... sorry!")

        self.engine.message_log.add_message(
            f"The {target.name} is struck by a magnificient beam of ancient power, taking {self.damage} damage"
        )
        self.engine.message_log.add_message(
            f"The rune shatters!"
        )
        target.fighter.take_damage(self.damage)
        self.consume()

class BowConsumable(Consumable):
    def __init__(self, damage: int):
        self.damage = damage

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot shoot yourself... sorry!")

        self.engine.message_log.add_message(
            f"The {target.name} is struck by the arrow, taking {self.damage} damage"
        )
        self.engine.message_log.add_message(
            f"The bow snaps!"
        )
        target.fighter.take_damage(self.damage)
        self.consume()

class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")

class TrickHealing(HealingConsumable):
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)
        self.engine.message_log.add_message(
            f"The potion was a trick! You drink the {self.parent.name}, and lose {amount_recovered} HP!",
            (200, 5, 0),
        )
        self.consume()
class DefenseConsumable(Consumable):
    def __init__(
            self,
            amount: int,
            number_of_turns: int,
    ):
        self.amount = amount
        self.number_of_turns = number_of_turns

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        if not isinstance(consumer.ai, components.ai.DefenseModifier) or not isinstance(consumer.ai, components.ai.PowerModifier):
            if (self.amount > 0):
                consumer.fighter.base_defense += self.amount
                self.engine.message_log.add_message(
                    f"You gain a defense bonus of {self.amount} for {self.number_of_turns} turns!",
                    color.status_effect_applied
                )
            else:
                consumer.fighter.base_defense += self.amount
                self.engine.message_log.add_message(
                    f"The potion was a trick, your feet begin to drag! "
                    f"You lose {self.amount} defense for {self.number_of_turns} turns!",
                    (200, 5, 0)
                )
            consumer.ai = components.ai.DefenseModifier(
                entity=consumer,
                previous_ai=consumer.ai,
                turns_remaining=self.number_of_turns,
                amount=self.amount,
            )
            self.consume()
        else:
            self.engine.message_log.add_message(
                f"You must wait for your current status effect to wear off!",
                (255,255,255)
            )

class PowerConsumable(DefenseConsumable):
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        if not isinstance(consumer.ai, components.ai.DefenseModifier) or not isinstance(consumer.ai, components.ai.PowerModifier):
            consumer = action.entity
            if self.amount > 0:
                consumer.fighter.base_power += self.amount
                self.engine.message_log.add_message(
                    f"You gain a power bonus of {self.amount} for {self.number_of_turns} turns!",
                    color.status_effect_applied
                )
            else:
                consumer.fighter.base_power += self.amount
                self.engine.message_log.add_message(
                    f"The potion was a trick! You lose {self.amount} power for {self.number_of_turns} turns!",
                    (200, 5, 0)
                )
            consumer.ai = components.ai.PowerModifier(
                entity=consumer,
                previous_ai=consumer.ai,
                turns_remaining=self.number_of_turns,
                amount=self.amount,
            )
            self.consume()
        else:
            self.engine.message_log.add_message(
                f"You must wait for your current status effect to wear off!",
                (255, 255, 255)
            )

class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see")

        target_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage"
                )
                actor.fighter.take_damage(self.damage)
                target_hit = True
        if not target_hit:
            raise Impossible("There are no targets in the radius")
        self.consume()

class TimeStopConsumable(Consumable):
    def __init__(self, number_of_turns: int, radius: int):
        self.number_of_turns = number_of_turns
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_hit = False
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see")

        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                if (actor.name is not "Player"):
                    self.engine.message_log.add_message(
                        f"The {actor.name} is stuck in the sands of time, for {self.number_of_turns} turns!"
                    )
                    actor.ai = components.ai.TimeStopAI(
                        entity=actor,
                        previous_ai=actor.ai,
                        turns_remaining=self.number_of_turns,
                    )
                    target_hit = True
        if not target_hit:
            raise Impossible("There are no targets in the radius")
        self.consume()

class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, max_range: int):
        self.damage = damage
        self.max_range = max_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.max_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lightning bold strikes the {target.name} with a loud crack for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike")

"""
The Staffs here are pseudo consumables. 
They hold the same function in inventory, but they are reusable items that won't dissappear after one use
"""
class Staff(Consumable):
    def __init__(self, damage: int):
        self.damage = damage

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot shoot yourself... sorry!")

        self.engine.message_log.add_message(
            f"A glowing ball of magic launches from the staff to strike {target.name}, taking {self.damage} damage"
        )
        target.fighter.take_damage(self.damage)

class ExplosiveStaff(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target_xy = action.target_xy

        target_hit = False
        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see")

        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"An explosive ball of magic launches from the staff to strike {actor.name}, taking {self.damage} damage"
                )
                actor.fighter.take_damage(self.damage)
                target_hit = True
        if not target_hit:
            raise Impossible("There are no targets in the radius")

class EndStaff(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target_xy = action.target_xy

        target_hit = False
        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see")

        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"Staggering mythic power unlike you have ever seen flies from the staff to strike {actor.name}, "
                    f"taking {self.damage} damage and dazing them!"
                )
                actor.fighter.take_damage(self.damage)
                actor.ai = components.ai.ConfusedEnemy(
                    entity=actor,
                    previous_ai=actor.ai,
                    turns_remaining=1,
                )
                target_hit = True
        if not target_hit:
            raise Impossible("There are no targets in the radius")