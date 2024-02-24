import itertools
import math

from lib.planners.halls.base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Building, Tile


class ThinHallPlanner(BaseHallPlanner):

  def __init__(self, has_crystals, *args):
    self.has_crystals = has_crystals
    super().__init__(*args)

  @property
  def inspect_color(self):
    return (0x44, 0x00, 0x08)

  @property
  def pearl_radius(self):
    return 0

  def _get_expected_crystals(self):
    if self.has_crystals:
      def d():
        for a, b in itertools.pairwise(self.baseplates):
          x1, y1 = a.center
          x2, y2 = b.center
          dx = x1 - x2
          dy = y1 - y2
          yield math.sqrt(dx * dx + dy * dy)
        yield -1 * self.baseplates[0].pearl_radius
        yield -1 * self.baseplates[1].pearl_radius
      mean = sum(d()) * self._stem.crystal_richness / 2
      if mean > 0:
        return self.rng['conquest.expected_crystals'].beta_int(
            a=5, b=2, min=0, max=mean * 1.25)
    return 0

  def fine_crystals(self, diorama):
    if not self.has_crystals:
      return
    rng = self.rng['fine.place_crystals']
    t = tuple(
        pearl_info.pos for pearl_info in self.pearl.inner if diorama.tiles.get(
            pearl_info.pos) in (
            Tile.DIRT,
            Tile.LOOSE_ROCK,
            Tile.HARD_ROCK))
    if t:
      for _ in range(self.expected_crystals):
        x, y = rng.beta_choice(t, a=2, b=2)
        existing = diorama.crystals.get((x, y), 0)
        if existing >= 3 and diorama.tiles.get((x, y)) != Tile.CRYSTAL_SEAM:
          diorama.tiles[x, y] = Tile.CRYSTAL_SEAM
          diorama.crystals[x, y] = existing - 3
        else:
          diorama.crystals[x, y] = existing + 1


def bids(stem, conquest):
  if stem.fluid_type is None:
    yield (0.2, lambda: ThinHallPlanner(False, stem, Oysters.OPEN))
    yield (0.1, lambda: ThinHallPlanner(True, stem, Oysters.FILLED))
    if conquest.expected_crystals > (
        0 +
        Building.Type.POWER_STATION.crystals +
        Building.Type.SUPPORT_STATION.crystals + 1 +
        Building.Type.SUPER_TELEPORT.crystals + 1 +
        5):
      yield (0.4, lambda: ThinHallPlanner(True, stem, Oysters.HARD_ROCK))


class Oysters:
  OPEN = Oyster('Open').layer(Layer.FLOOR)
  FILLED = Oyster('Filled').layer(Layer.LOOSE_ROCK)
  HARD_ROCK = Oyster('Hard Rock').layer(Layer.HARD_ROCK)
