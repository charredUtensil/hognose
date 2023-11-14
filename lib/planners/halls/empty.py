from .base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class EmptyHallPlanner(BaseHallPlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)

def bids(stem, conquest):
  pr = stem.pearl_radius
  if stem.fluid_type == Tile.WATER:
    yield (1, lambda: EmptyHallPlanner(stem, conquest, Oysters.RIVER))
  elif stem.fluid_type == Tile.LAVA:
    yield (1, lambda: EmptyHallPlanner(stem, conquest, Oysters.LAVA_RIVER))
  else:
    if pr < 7:
      yield (1, lambda: EmptyHallPlanner(stem, conquest, Oysters.FILLED))
    yield (1, lambda: EmptyHallPlanner(stem, conquest, Oysters.OPEN))

class Oysters:
  OPEN = (
    Oyster('Open')
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.AT_MOST_LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )
  FILLED = (
    Oyster('Filled')
      .layer(Layer.DIRT, grow=1)
      .layer(Layer.LOOSE_OR_HARD_ROCK)
      .layer(Layer.VOID, grow=1)
  )
  RIVER = (
    Oyster('River')
      .layer(Layer.WATER, width=2, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK)
      .layer(Layer.VOID, grow=1)
  )
  LAVA_RIVER = (
    Oyster('Lava River')
      .layer(Layer.LAVA, width=2, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK, width=0, grow=1)
      .layer(Layer.VOID, grow=1)
  )