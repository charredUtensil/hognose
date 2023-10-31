class Tile:

  def __init__(self, export_value, is_wall, inspect_color):
    self.export_value = export_value
    self.is_wall = is_wall
    self.inspect_color = inspect_color

  def __repr__(self):
    return f'Tile #{self.export_value}'

# Colors from https://github.com/trigger-segfault/legorockraiders-analysis
Tile.FLOOR         = Tile( 1, False, (0x2D, 0x00, 0x4B))
Tile.LAVA          = Tile( 6, False, (0xFF, 0x5A, 0x00))
Tile.WATER         = Tile(11, False, (0x00, 0x2F, 0xB5))
Tile.FOUNDATION    = Tile(14, False, (0xBF, 0xBF, 0xBF))
Tile.POWER_PATH    = Tile(24, False, (0x9D, 0x9B, 0x00))
Tile.DIRT          = Tile(26,  True, (0xAD, 0x59, 0xEF))
Tile.LOOSE_ROCK    = Tile(30,  True, (0x94, 0x3C, 0xC3))
Tile.HARD_ROCK     = Tile(34,  True, (0x73, 0x1C, 0xAD))
Tile.SOLID_ROCK    = Tile(38,  True, (0x80, 0x00, 0x80))
Tile.CRYSTAL_SEAM  = Tile(42,  True, (0xB5, 0xFF, 0x00))
Tile.ORE_SEAM      = Tile(46,  True, (0x9C, 0x41, 0x08))
Tile.RECHARGE_SEAM = Tile(50,  True, (0xFF, 0xFF, 0x00))
