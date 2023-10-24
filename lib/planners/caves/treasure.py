import math

from .base import BaseCavePlanner
from lib.planners.onions import OnionFactoryBuilder as gfb
from lib.plastic import Tile

class TreasureCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, gradient_factory):
    super().__init__(stem)
    self.onion = gradient_factory.create(self._context, self._id)
    self.expected_crystals = math.floor(
      conquest.expected_crystals * self.rng.normal(0.4, 0.1))

  def fine(self, canvas):
    cx, cy = self.rng.choice(self.baseplates).center
    for _ in range(self.expected_crystals):
      x, y = self.rng.point_in_circle(2, (cx, cy))
      x = math.floor(x)
      y = math.floor(y)
      canvas.crystals[x, y] += 1

  @classmethod
  def bids(cls, stem, conquest):
    if len(conquest.intersecting(stem)) <= 2:
      yield (1, lambda: cls(stem, conquest, GRADIENT_FACTORY))


GRADIENT_FACTORY = (gfb()
    .w(3, 5, Tile.FLOOR)
    .w(1, 2, Tile.LOOSE_ROCK)
    .w(0, 2, Tile.HARD_ROCK)
    .build()
)