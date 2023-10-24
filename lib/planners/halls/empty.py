from .base import BaseHallPlanner
from lib.planners.onions import OnionFactoryBuilder as gfb
from lib.plastic import Tile

class EmptyHallPlanner(BaseHallPlanner):

  def __init__(self, stem, conquest, gradient_factory):
    super().__init__(stem)
    self.onion = gradient_factory.create(self._context, self._id)

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type == 2:
      yield (1, lambda: cls(stem, conquest, Gradients.RIVER))
    elif stem.fluid_type == 6:
      yield (1, lambda: cls(stem, conquest, Gradients.LAVA_RIVER))
    else:
      yield (1, lambda: cls(stem, conquest, Gradients.OPEN_SPACE))
      yield (1, lambda: cls(stem, conquest, Gradients.FILLED))


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
  RIVER = (gfb()
      .w(1, 5, Tile.WATER)
      .w(0, 2, Tile.HARD_ROCK)
      .build()
  )
  LAVA_RIVER = (gfb()
      .w(1, 5, Tile.LAVA)
      .w(0, 2, Tile.HARD_ROCK)
      .build()
  )