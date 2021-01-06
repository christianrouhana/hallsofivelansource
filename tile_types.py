from typing import Tuple

import numpy as np

#tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
    [
        ("ch", np.int32),
        ("fg", "3B"), # 3 unsigned bytes, for RGB colors
        ("bg", "3B"),
    ]
)

# Tile struct used for statistically defined tile data
tile_dt = np.dtype(
    [
        ("walkable", np.bool), # true -> can be walked on
        ("transparent", np.bool), # true -> tile does not block FOV
        ("dark", graphic_dt), #graphics for when not in FOV
        ("light", graphic_dt), #graphics for when in FOV
    ]
)

def new_tile(
        *, #enforce use of keywords, so paramater order does not matter
        walkable: int,
        transparent:int,
        dark: Tuple[int, Tuple[int,int,int], Tuple[int,int,int]],
        light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

# SHROUD IS UNEXPLORED && UNSEEN TILES
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype = graphic_dt)

late_floor = new_tile(
    walkable = True,
    transparent=True,
    dark=(ord("\""), (60,0,0), (15,15,15)),
    light=(ord("\""), (100, 0, 0), (45, 45, 45)),
)

floor = new_tile(
    walkable = True,
    transparent=True,
    dark=(ord("."), (70,70,70), (15,5,0)),
    light=(ord("."), (230, 100, 25), (50, 20, 0)),
)

late_wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("0"), (15,15,15), (30,30,30)),
    light=(ord("0"), (30, 30, 30), (100, 100, 100)),
)

wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (60,30,10), (40,17,10)),
    light=(ord("#"), (120, 70, 0), (90, 50, 0)),
)

late_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (60,0,0), (15,15,15)),
    light=(ord(">"), (130,0,0), (100,100,100))
)

down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (70,70,70), (50,20,0)),
    light=(ord(">"), (250,170,0), (150,100,0))
)

win_game = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("^"), (140,140,0), (60,60,60)),
    light=(ord("^"), (250,240,0), (150,150,150))
)