from typing import Literal

import enum

class Tile(enum.Enum):

  def __init__(self, export_value, is_wall, passable_by_miner, inspect_color):
    super().__init__()
    self.export_value = export_value
    self.is_wall = is_wall
    self.passable_by_miner = passable_by_miner
    self.inspect_color = inspect_color

  # Basic floor tiles
  FLOOR         = ( 1, False,  True, (0x2D, 0x00, 0x4B))
  LAVA          = ( 6, False, False, (0xFF, 0x5A, 0x00))
  WATER         = (11, False, False, (0x00, 0x2F, 0xB5))
  # Basic wall tiles
  DIRT          = (26,  True,  True, (0xAD, 0x59, 0xEF))
  LOOSE_ROCK    = (30,  True,  True, (0x94, 0x3C, 0xC3))
  HARD_ROCK     = (34,  True,  True, (0x73, 0x1C, 0xAD))
  SOLID_ROCK    = (38,  True, False, (0x80, 0x00, 0x80))
  # Floor tiles
  RUBBLE_1      = ( 2, False,  True, (0x18, 0x00, 0x32))
  RUBBLE_2      = ( 3, False,  True, (0x18, 0x00, 0x32))
  RUBBLE_3      = ( 4, False,  True, (0x18, 0x00, 0x32))
  RUBBLE_4      = ( 5, False,  True, (0x18, 0x00, 0x32))
  FOUNDATION    = (14, False,  True, (0xBF, 0xBF, 0xBF))
  POWER_PATH    = (24, False,  True, (0x9D, 0x9B, 0x00))
  # Wall tiles
  CRYSTAL_SEAM  = (42,  True,  True, (0xB5, 0xFF, 0x00))
  ORE_SEAM      = (46,  True,  True, (0x9C, 0x41, 0x08))
  RECHARGE_SEAM = (50,  True, False, (0xFF, 0xFF, 0x00))

# Colors from https://github.com/trigger-segfault/legorockraiders-analysis

BasicTile = Literal[
    Tile.FLOOR,
    Tile.LAVA,
    Tile.WATER,
    Tile.DIRT,
    Tile.LOOSE_ROCK,
    Tile.HARD_ROCK,
    Tile.SOLID_ROCK,
]
