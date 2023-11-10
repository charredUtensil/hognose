import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class BaseHallPlanner(SomaticPlanner):
  
  @property
  def baroqueness(self) -> float:
    return self.context.hall_baroqueness

  def pearl_nucleus(self):
    return self.walk_stream()

  def fine(self, diorama):
    pass