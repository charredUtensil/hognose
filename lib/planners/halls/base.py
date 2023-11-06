import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class BaseHallPlanner(SomaticPlanner):
  
  @property
  def baroqueness(self) -> float:
    return self.context.hall_baroqueness

  def walk(self):
    r = min(min(bp.width, bp.height) for bp in self.baseplates) // 2
    self._pearl = tuple(self.walk_pearl(self.walk_stream(), r))
    return self._pearl

  def pearl_nucleus(self):
    return self.walk_stream()

  def fine(self, diorama):
    pass