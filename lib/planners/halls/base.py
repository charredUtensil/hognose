import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class BaseHallPlanner(SomaticPlanner):
  
  @property
  def baroqueness(self) -> float:
    return self.context.hall_baroqueness

  def _get_expected_crystals(self):
    return 0

  def pearl_nucleus(self):
    return self.walk_stream()

  def fine(self, diorama):
    self.fine_landslides(diorama)
    self.fine_erosion(diorama)

  def fine_landslides(self, diorama):
    if self.rng['fine.place_landslides'].chance(self.context.hall_landslide_chance):
      freq = self.context.hall_landslide_freq * sum(1 for _ in self.walk_stream())
      self.place_landslides(diorama, freq)

  def script(self, diorama):
    pass