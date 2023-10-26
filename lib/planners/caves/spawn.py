import math

from .base import BaseCavePlanner
from lib.planners.onions import OnionFactoryBuilder as gfb
from lib.plastic import Building, Tile

class SpawnCavePlanner(BaseCavePlanner):
  
  def __init__(self, stem, conquest, gradient_factory):
    super().__init__(stem)
    self.expected_crystals = max(0, math.floor(self.rng.normal(mean=5, stddev=1)))
    self.onion = gradient_factory.create(self._context, self._id)

    lot = self.rng.choice(self.baseplates)
    self._toolstore = tuple(
      math.floor(n) for n in self.rng.point_in_circle(3, lot.center))

  def fine(self, diorama):
    super().fine(diorama)
    diorama.tiles[self._toolstore] = Tile.FOUNDATION
    diorama.tiles[self._toolstore[0], self._toolstore[1] - 1] = Tile.FOUNDATION
    diorama.buildings.append(Building(Building.TOOL_STORE, self._toolstore, 0))
    diorama.open_cave_flags.add(self._toolstore)
    diorama.camera_origin = self._toolstore

  @classmethod
  def bids(cls, stem, conquest):
    yield (1, lambda: cls(stem, conquest, GRADIENT_FACTORY))

GRADIENT_FACTORY = (gfb()
    .w(3, 5, Tile.FLOOR)
    .w(1, 2, Tile.LOOSE_ROCK)
    .w(0, 2, Tile.HARD_ROCK)
    .build()
)