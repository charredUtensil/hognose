from .base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class EmptyHallPlanner(BaseHallPlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type == 2:
      yield (1, lambda: cls(stem, conquest, Oysters.RIVER))
    elif stem.fluid_type == 6:
      yield (1, lambda: cls(stem, conquest, Oysters.LAVA_RIVER))
    else:
      yield (1, lambda: cls(stem, conquest, Oysters.OPEN_SPACE))
      yield (1, lambda: cls(stem, conquest, Oysters.FILLED))

class Oysters:
  OPEN_SPACE = (
    Oyster('Open')
      .layer(Layer.OPEN, grow=2)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK)
  )
  FILLED = (
    Oyster('Filled')
      .layer(Layer.DIRT, grow=1)
      .layer(Layer.HARD_ROCK)
  )
  RIVER = (
    Oyster('River')
      .layer(Layer.WATER, width=2, grow=1)
      .layer(Layer.HARD_ROCK)
  )
  LAVA_RIVER = (
    Oyster('Lava River')
      .layer(Layer.LAVA, width=3, grow=1)
      .layer(Layer.HARD_ROCK)
  )