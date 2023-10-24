import math

from .base import BaseCavePlanner
from lib.planners.onions import OnionFactoryBuilder as gfb
from lib.plastic import Tile

class EmptyCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, gradient_factory):
    super().__init__(stem)
    self.onion = gradient_factory.create(self._context, self._id)
    self.expected_crystals = min(0, math.floor(
      self.rng.normal(15, 5)))

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type == 2:
      yield (1, lambda: cls(stem, conquest, Gradients.LAKE))
    elif stem.fluid_type == 6:
      yield (1, lambda: cls(stem, conquest, Gradients.LAVA_LAKE))
    else:
      yield (1, lambda: cls(stem, conquest, Gradients.OPEN_SPACE))
      yield (0.04, lambda: cls(stem, conquest, Gradients.FILLED))

class Gradients:
  OPEN_SPACE = (gfb()
      .w(1, 3, Tile.FLOOR)
      .w(0, 2, Tile.LOOSE_ROCK)
      .w(0, 2, Tile.HARD_ROCK)
      .build()
  )
  FILLED = (gfb()
      .w(1, 5, Tile.LOOSE_ROCK)
      .w(0, 2, Tile.HARD_ROCK)
      .build()
  )
  LAKE = (gfb()
      .w(1, 3, Tile.WATER)
      .w(0, 1, Tile.FLOOR)
      .w(0, 2, Tile.LOOSE_ROCK)
      .w(0, 2, Tile.HARD_ROCK)
      .build()
  )
  LAVA_LAKE = (gfb()
      .w(1, 6, Tile.LAVA)
      .w(0, 2, Tile.HARD_ROCK)
      .build()
  )