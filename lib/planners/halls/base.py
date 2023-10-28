import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class BaseHallPlanner(SomaticPlanner):

  def walk(self):
    r = min(min(bp.width, bp.height) for bp in self.baseplates) // 2
    self._pearl = tuple(self.walk_pearl(self.walk_stream(), r))
    return self._pearl

  def rough(self, tiles):
    self.walk()
    nacre = self.oyster.create(self._pearl[-1][-1])
    for (x, y), layer in self._pearl:
      tiles[x, y] = nacre.layers[layer]._place

  def fine(self, diorama):
    pass