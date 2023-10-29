import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class EmptyCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = max(0, math.floor(
      self.rng.normal(15, 5)))

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type == 2:
      yield (1, lambda: cls(stem, conquest, Oysters.LAKE))
    elif stem.fluid_type == 6:
      yield (1, lambda: cls(stem, conquest, Oysters.LAVA_LAKE))
    else:
      yield (1, lambda: cls(stem, conquest, Oysters.OPEN_SPACE))
      yield (0.04, lambda: cls(stem, conquest, Oysters.FILLED))

class Oysters:
  OPEN_SPACE = (
    Oyster('Open')
      .layer(Layer.OPEN, grow=2)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )
  FILLED = (
    Oyster('Filled')
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK)
  )
  LAKE = (
    Oyster('Lake')
      .layer(Layer.WATER, grow=2)
      .layer(Layer.OPEN, shrink=1, grow=1)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.HARD_ROCK)
  )
  LAVA_LAKE = (
    Oyster('Lava Lake')
      .layer(Layer.LAVA, grow=2)
      .layer(Layer.OPEN, grow=1)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK)
  )