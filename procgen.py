from __future__ import annotations

import random
from typing import Iterator, Tuple, List, TYPE_CHECKING, Dict
import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from engine import Entity

max_items_by_floor = [
    (1,1),
    (3,2),
    (6,3),
    (8,4),
    (10,5),
]

max_monsters_by_floor=[
    (1,1),
    (2,2),
    (4,4),
    (8,6),
    (10,7),
]
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
   1: [
       (entity_factories.health_potion, 30), (entity_factories.super_health_potion, 10),
       (entity_factories.confusion_scroll, 15), (entity_factories.sword, 10), (entity_factories.chain_mail,1)
   ],
   2: [
       (entity_factories.sword, 15), (entity_factories.chain_mail, 10), (entity_factories.health_potion, 30),
       (entity_factories.super_health_potion, 15), (entity_factories.confusion_scroll, 20),
       (entity_factories.lightning_scroll, 10), (entity_factories.power_potion, 10),
       (entity_factories.defense_potion, 10), (entity_factories.old_bow, 10)
   ],
   3: [
       (entity_factories.sword, 25), (entity_factories.diamond_sword, 1), (entity_factories.knight_armor, 1),
       (entity_factories.chain_mail, 20), (entity_factories.health_potion, 35),
       (entity_factories.super_health_potion, 20), (entity_factories.confusion_scroll, 25),
       (entity_factories.lightning_scroll, 15), (entity_factories.power_potion, 15),
       (entity_factories.defense_potion, 15), (entity_factories.old_bow, 15), (entity_factories.trick_power_potion, 10),
       (entity_factories.trick_defense_potion, 10), (entity_factories.trick_health_potion, 10)
   ],
   4: [
       (entity_factories.sword, 25), (entity_factories.diamond_sword, 15), (entity_factories.knight_armor, 15),
       (entity_factories.chain_mail, 20), (entity_factories.health_potion, 35),
       (entity_factories.super_health_potion, 25), (entity_factories.confusion_scroll, 30),
       (entity_factories.lightning_scroll, 20), (entity_factories.power_potion, 20),
       (entity_factories.defense_potion, 20), (entity_factories.old_bow, 15), (entity_factories.trick_power_potion, 15),
       (entity_factories.trick_defense_potion, 15), (entity_factories.trick_health_potion, 15),
       (entity_factories.beam_rune, 5), (entity_factories.lesser_staff, 5), (entity_factories.adamantine_armor, 1),
       (entity_factories.adamantine_sword, 1), (entity_factories.fireball_scroll, 15),
       (entity_factories.time_stop_scroll, 5)
   ],
   5: [
       (entity_factories.sword, 10), (entity_factories.diamond_sword, 20), (entity_factories.knight_armor, 20),
       (entity_factories.chain_mail, 10), (entity_factories.health_potion, 30),
       (entity_factories.super_health_potion, 30), (entity_factories.confusion_scroll, 30),
       (entity_factories.lightning_scroll, 25), (entity_factories.power_potion, 25),
       (entity_factories.defense_potion, 25), (entity_factories.old_bow, 25), (entity_factories.trick_power_potion, 15),
       (entity_factories.trick_defense_potion, 15), (entity_factories.trick_health_potion, 15),
       (entity_factories.beam_rune, 10), (entity_factories.lesser_staff, 10), (entity_factories.adamantine_armor, 10),
       (entity_factories.adamantine_sword, 10), (entity_factories.fireball_scroll, 20),
       (entity_factories.time_stop_scroll, 15)
   ],
   6: [
       (entity_factories.sword, 1), (entity_factories.diamond_sword, 15), (entity_factories.knight_armor, 15),
       (entity_factories.chain_mail, 1), (entity_factories.health_potion, 30),
       (entity_factories.super_health_potion, 30), (entity_factories.confusion_scroll, 20),
       (entity_factories.lightning_scroll, 30), (entity_factories.power_potion, 30),
       (entity_factories.defense_potion, 30), (entity_factories.old_bow, 15), (entity_factories.trick_power_potion, 15),
       (entity_factories.trick_defense_potion, 15), (entity_factories.trick_health_potion, 15),
       (entity_factories.beam_rune, 15), (entity_factories.lesser_staff, 10), (entity_factories.adamantine_armor, 25),
       (entity_factories.adamantine_sword, 25), (entity_factories.fireball_scroll, 25),
       (entity_factories.runic_armor, 5), (entity_factories.beam_sword, 5), (entity_factories.time_stop_scroll, 25),
       (entity_factories.explosive_staff, 10),
   ],
   7: [
       (entity_factories.sword, 0), (entity_factories.diamond_sword, 15), (entity_factories.knight_armor, 15),
       (entity_factories.chain_mail, 0), (entity_factories.health_potion, 25),
       (entity_factories.super_health_potion, 35), (entity_factories.confusion_scroll, 20),
       (entity_factories.lightning_scroll, 30), (entity_factories.power_potion, 30),
       (entity_factories.defense_potion, 30), (entity_factories.old_bow, 15), (entity_factories.trick_power_potion, 15),
       (entity_factories.trick_defense_potion, 15), (entity_factories.trick_health_potion, 15),
       (entity_factories.beam_rune, 15), (entity_factories.lesser_staff, 10), (entity_factories.adamantine_armor, 25),
       (entity_factories.adamantine_sword, 20), (entity_factories.fireball_scroll, 20),
       (entity_factories.runic_armor, 20), (entity_factories.beam_sword, 20), (entity_factories.explosive_staff, 20),
   ],
   8: [
       (entity_factories.diamond_sword, 5), (entity_factories.knight_armor, 5),
       (entity_factories.health_potion, 20), (entity_factories.super_health_potion, 40),
       (entity_factories.confusion_scroll, 20), (entity_factories.lightning_scroll, 30),
       (entity_factories.power_potion, 30), (entity_factories.defense_potion, 30), (entity_factories.old_bow, 15),
       (entity_factories.trick_power_potion, 15), (entity_factories.trick_defense_potion, 15),
       (entity_factories.trick_health_potion, 15), (entity_factories.beam_rune, 20), (entity_factories.lesser_staff, 20)
       , (entity_factories.adamantine_armor, 25), (entity_factories.adamantine_sword, 20),
       (entity_factories.fireball_scroll, 20), (entity_factories.runic_armor, 30), (entity_factories.beam_sword, 30),
       (entity_factories.explosive_staff, 25), (entity_factories.end_staff, 1)
   ],
   9: [
       (entity_factories.diamond_sword, 0), (entity_factories.knight_armor, 0),
       (entity_factories.health_potion, 30), (entity_factories.super_health_potion, 30),
       (entity_factories.confusion_scroll, 20), (entity_factories.lightning_scroll, 30),
       (entity_factories.power_potion, 30), (entity_factories.defense_potion, 30), (entity_factories.old_bow, 10),
       (entity_factories.trick_power_potion, 15), (entity_factories.trick_defense_potion, 15),
       (entity_factories.trick_health_potion, 15), (entity_factories.beam_rune, 20), (entity_factories.lesser_staff, 20)
       , (entity_factories.adamantine_armor, 25), (entity_factories.adamantine_sword, 20),
       (entity_factories.fireball_scroll, 20), (entity_factories.runic_armor, 35), (entity_factories.beam_sword, 35),
       (entity_factories.explosive_staff, 30), (entity_factories.end_staff, 1)
   ],
   10: [
       (entity_factories.health_potion, 15,), (entity_factories.super_health_potion, 40),
       (entity_factories.confusion_scroll, 15), (entity_factories.lightning_scroll, 20),
       (entity_factories.power_potion, 30), (entity_factories.defense_potion, 30), (entity_factories.old_bow, 10),
       (entity_factories.trick_power_potion, 15), (entity_factories.trick_defense_potion, 15),
       (entity_factories.trick_health_potion, 15), (entity_factories.beam_rune, 20), (entity_factories.lesser_staff, 10)
       , (entity_factories.adamantine_armor, 0), (entity_factories.adamantine_sword, 0),
       (entity_factories.fireball_scroll, 10), (entity_factories.runic_armor, 35), (entity_factories.beam_sword, 35),
       (entity_factories.explosive_staff, 30), (entity_factories.end_staff, 35)
   ]
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    1: [
        (entity_factories.goblin, 15), (entity_factories.orc, 35), (entity_factories.jackal, 20),
        (entity_factories.goblin_archer, 10)
    ],
    2: [
        (entity_factories.goblin, 15), (entity_factories.orc, 35), (entity_factories.jackal, 20),
        (entity_factories.goblin_archer, 10), (entity_factories.drone, 10)
    ],
    3: [
        (entity_factories.goblin, 20), (entity_factories.orc, 35), (entity_factories.jackal, 20),
        (entity_factories.goblin_archer, 15), (entity_factories.drone, 20), (entity_factories.guardian, 15),
        (entity_factories.troll, 15), (entity_factories.warden, 1)
    ],
    4: [
        (entity_factories.goblin, 20), (entity_factories.orc, 35), (entity_factories.jackal, 20),
        (entity_factories.goblin_archer, 15), (entity_factories.drone, 25), (entity_factories.guardian, 20),
        (entity_factories.troll, 15), (entity_factories.warden, 1)
    ],
    5: [
        (entity_factories.goblin, 20), (entity_factories.orc, 35), (entity_factories.jackal, 20),
        (entity_factories.goblin_archer, 15), (entity_factories.drone, 25), (entity_factories.guardian, 20),
        (entity_factories.troll, 15), (entity_factories.warden, 10),
    ],
    6: [
        (entity_factories.goblin, 15), (entity_factories.orc, 20), (entity_factories.jackal, 15),
        (entity_factories.goblin_archer, 15), (entity_factories.drone, 25), (entity_factories.guardian, 25),
        (entity_factories.troll, 25), (entity_factories.warden, 15), (entity_factories.corrupted_wizard, 10),
    ],
    7: [
        (entity_factories.goblin, 10), (entity_factories.orc, 10), (entity_factories.jackal, 10),
        (entity_factories.goblin_archer, 10), (entity_factories.drone, 25), (entity_factories.guardian, 25),
        (entity_factories.troll, 25), (entity_factories.warden, 15), (entity_factories.corrupted_wizard, 15),
        (entity_factories.enchanted_statue, 10),
    ],
    8: [
        (entity_factories.goblin, 5), (entity_factories.orc, 5), (entity_factories.jackal, 5),
        (entity_factories.goblin_archer, 5), (entity_factories.drone, 30), (entity_factories.guardian, 30),
        (entity_factories.troll, 35), (entity_factories.warden, 20), (entity_factories.corrupted_wizard, 20),
        (entity_factories.enchanted_statue, 10),
    ],
    9: [
        (entity_factories.goblin, 0), (entity_factories.orc, 0), (entity_factories.jackal, 0),
        (entity_factories.goblin_archer, 0), (entity_factories.drone, 30), (entity_factories.guardian, 30),
        (entity_factories.troll, 35), (entity_factories.warden, 25), (entity_factories.corrupted_wizard, 25),
        (entity_factories.enchanted_statue, 10),(entity_factories.agent_of_ivelan, 5)
    ],
    10: [
        (entity_factories.drone, 35), (entity_factories.guardian, 35),
        (entity_factories.troll, 35), (entity_factories.warden, 20), (entity_factories.corrupted_wizard, 25),
        (entity_factories.enchanted_statue, 15),(entity_factories.agent_of_ivelan, 5)
    ]
}

def get_max_value_for_floor(
        weighted_chances_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in weighted_chances_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value
    return current_value

def get_entities_at_random(
   weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
   number_of_entities: int,
   floor: int,
) -> List[Entity]:
   entity_weighted_chances = {}

   for key, values in weighted_chances_by_floor.items():
       if key > floor:
           break
       else:
           for value in values:
               entity = value[0]
               weighted_chance = value[1]

               entity_weighted_chances[entity] = weighted_chance

   entities = list(entity_weighted_chances.keys())
   entity_weighted_chance_values = list(entity_weighted_chances.values())

   chosen_entities = random.choices(
       entities, weights=entity_weighted_chance_values, k=number_of_entities
   )

   return chosen_entities

class RectangularRoom:
    def __init__(self, x:int, y:int, width:int, height: int):
        self.x1 = x  # top left corner
        self.y1 = y
        self.x2 = x + width  # bottom right corner computer from width & height
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """returns true if this room overlaps with another rectangular room"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y1 >= other.y1
        )

def place_entities(
        room: RectangularRoom,
        dungeon: GameMap,
        floor_number:int,
) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x ==x and entity.y ==y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)

def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """return an l shaped tunnel between two points (tuple(int))"""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5: # 50% chance
        # move horizontal, then vertical
        corner_x, corner_y = x2, y1
    else:
        # move vertically, then horizontally
        corner_x, corner_y = x1, y2

    # generate coord for this tunnel
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y

def generate_dungeon(
        max_rooms:int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        engine: Engine,
) -> GameMap:
    """Generate a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0,0)
    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # RectangularRoom class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # room intersects, goto next valid attempt
        # if there are no interesects, valid room

        # dig rooms
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # player starting room
            player.place(*new_room.center, dungeon)
        else: # all rooms after the first
            # Dig tunnel between this room and previous room
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
            center_of_last_room = new_room.center
        place_entities(new_room, dungeon, engine.game_world.current_floor)
        if (engine.game_world.current_floor != 10):
            dungeon.tiles[center_of_last_room] = tile_types.down_stairs
            dungeon.downstairs_location = center_of_last_room
        else:
            dungeon.tiles[center_of_last_room] = tile_types.win_game
            dungeon.game_win = center_of_last_room
        # append new room to list
        rooms.append(new_room)
    if (engine.game_world.current_floor == 10):
        entity_factories.monolith.spawn(
            dungeon,
            center_of_last_room[0] + random.randint(0, 1),
            center_of_last_room[1] + random.randint(0, 1),
        )
    return dungeon