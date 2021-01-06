from __future__ import annotations

from typing import Iterable, TYPE_CHECKING, Iterator, Optional

import numpy as np
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap:
    def __init__(
            self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        if self.engine.game_world.current_floor < 6:
            self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        else:
            self.tiles = np.full((width, height), fill_value=tile_types.late_wall, order="F")
        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        ) #tiles player can see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        ) #tiles player has explored
        self.downstairs_location = (0,0)
        self.game_win = (0,0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors"""
        yield from(
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
            self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
        return None

    def in_bounds(self, x: int, y:int) -> bool:
        """return True if x and y are in bounds"""
        return 0 <= x <self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        renders the map
        if a tile is in "visible" draw with "light
        if it is not but is explored, draw with "dark"
        else SHROUD
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key = lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            #only print entities that are in FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x = entity.x, y = entity.y, string = entity.char, fg=entity.color
                )

class GameWorld:
    """holds settings for gamemap, and generates new map as player descends"""
    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            current_floor: int = 0
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )