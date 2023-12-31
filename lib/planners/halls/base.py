import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile
from lib.utils.geometry import plot_line

class BaseHallPlanner(SomaticPlanner):
  
  @property
  def baroqueness(self) -> float:
    return self.context.hall_baroqueness

  def _get_expected_crystals(self):
    return 0

  @property
  def pearl_radius(self):
    return min(min(bp.width, bp.height) for bp in self.baseplates) // 2

  def make_nucleus(self):
    def w():
      for a, b in itertools.pairwise(self.baseplates):
        yield from plot_line(a.center, b.center, contiguous=True)
    return {0: w()}

  def fine(self, diorama):
    self.fine_crystals(diorama)
    self.fine_landslides(diorama)
    self.fine_erosion(diorama)

  def fine_crystals(self, diorama):
    pass

  def fine_landslides(self, diorama):
    if self.rng['fine.place_landslides'].chance(self.context.hall_landslide_chance):
      freq = self.context.hall_landslide_freq * sum(1 for _ in self.pearl.nucleus)
      self.place_landslides(diorama, freq)

  def script(self, diorama):
    pass