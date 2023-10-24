import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class BaseHallPlanner(SomaticPlanner):

  def rough(self, tiles):
    for (x, y), (u, _) in self.walk_tube():
      if tiles.get((x, y)) not in (Tile.WATER, Tile.LAVA):
        for t, tile in self.onion.stops():
          if u < t:
            tiles[x, y] = tile
            break
  
  def fine(self, diorama):
    pass