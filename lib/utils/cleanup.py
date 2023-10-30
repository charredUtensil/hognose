from typing import Dict, Tuple

from lib.plastic import Tile

_FLOOR_TILES = frozenset((
    Tile.FLOOR,
    Tile.WATER,
    Tile.LAVA))

def patch(tiles: Dict[Tuple[int, int], Tile]):
  left   = min(x for x, y in tiles)
  right  = max(x for x, y in tiles)
  top    = min(y for x, y in tiles)
  bottom = max(y for x, y in tiles)
  for x in range(left, right + 1):
    for y in range(top, bottom + 1):
      if tiles.get((x, y)) in _FLOOR_TILES:
        continue
      neighbors = tuple(
          ((ox, oy), tiles.get((x + ox, y + oy), Tile.SOLID_ROCK))
          for (ox, oy)
          in ((0, -1), (0, 1), (-1, 0), (1, 0)))
      wall_neighbors = tuple(
          (ox, oy)
          for (ox, oy), tile
          in neighbors
          if tile not in _FLOOR_TILES)
      if len(wall_neighbors) > 1:
        continue
      if not wall_neighbors:
        wall_neighbors = ((0, -1),)
        tiles[x, y - 1] = Tile.DIRT
      ox, oy = wall_neighbors[0]
      # Right turn
      tiles[x - oy, y + ox] = Tile.DIRT
      # Remaining square
      if tiles.get((x + ox - oy, y + ox + oy)) in _FLOOR_TILES:
        tiles[x + ox - oy, y + ox + oy] = Tile.DIRT
      
      
        
          
