from .base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class ThinHallPlanner(BaseHallPlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem)
    self.oyster = oyster

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type is None:
      yield   (0.1, lambda: cls(stem, conquest, Oysters.FLOOR))
      yield   (0.2, lambda: cls(stem, conquest, Oysters.FILLED))
      if conquest.expected_crystals > (0 +
          + 2     # Power Station
          + 3 + 1 # Support Station (powered)
          + 4 + 1 # Super Teleport  (powered)
          + 5     # Granite Grinder
          ):
        yield (0.4, lambda: cls(stem, conquest, Oysters.HARD_ROCK))

class Oysters:
  FLOOR = Oyster().layer(Layer.FLOOR)
  FILLED = Oyster().layer(Layer.LOOSE_ROCK)
  HARD_ROCK = Oyster().layer(Layer.HARD_ROCK)