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
    self.fine_crystals(diorama)
    self.fine_landslides(diorama)
    self.fine_erosion(diorama)

  def fine_crystals(self, diorama):
    pass

  def fine_landslides(self, diorama):
    if self.rng['fine.place_landslides'].chance(self.context.hall_landslide_chance):
      freq = self.context.hall_landslide_freq * sum(1 for info in self.pearl if info.layer == 0)
      self.place_landslides(diorama, freq)

  def script(self, diorama):
    pass