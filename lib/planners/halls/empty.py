from .base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class EmptyHallPlanner(BaseHallPlanner):
  @property
  def inspect_color(self):
    return (0x77, 0x00, 0x10)

def bids(stem, conquest):
  pr = stem.pearl_radius
  if stem.fluid_type == Tile.WATER:
    yield (1, lambda: EmptyHallPlanner(stem, Oysters.RIVER))
    if pr > 1 and all(
        p.fluid_type == Tile.WATER for p in conquest.intersecting(stem)):
      yield (1, lambda: EmptyHallPlanner(stem, Oysters.STREAM))
  elif stem.fluid_type == Tile.LAVA:
    yield (1, lambda: EmptyHallPlanner(stem, Oysters.LAVA_RIVER))
  elif pr > 0:
    yield (1, lambda: EmptyHallPlanner(stem, Oysters.FILLED))
    yield (1, lambda: EmptyHallPlanner(stem, Oysters.OPEN))

class Oysters:
  OPEN = (
    Oyster('Open')
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.AT_MOST_LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK)
      .layer(Layer.VOID, grow=1)
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
  STREAM = (
    Oyster('Stream')
      .layer(Layer.WATER, grow=0.5)
      .layer(Layer.FLOOR, grow=0.25, shrink=1)
      .layer(Layer.DIRT_OR_LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK, shrink=1)
  )
  LAVA_RIVER = (
    Oyster('Lava River')
      .layer(Layer.LAVA, width=2, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK, width=0, grow=1)
      .layer(Layer.VOID, grow=1)
  )