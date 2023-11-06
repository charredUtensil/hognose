from .base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class ThinHallPlanner(BaseHallPlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)

  @property
  def pearl_radius(self):
    return 0

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type is None:
      yield   (0.1, lambda: cls(stem, conquest, Oysters.OPEN))
      yield   (0.2, lambda: cls(stem, conquest, Oysters.FILLED))
      if conquest.expected_crystals > (0 +
          + 2     # Power Station
          + 3 + 1 # Support Station (powered)
          + 4 + 1 # Super Teleport  (powered)
          + 5     # Granite Grinder
          ):
        yield (0.4, lambda: cls(stem, conquest, Oysters.HARD_ROCK))

class Oysters:
  OPEN = Oyster('Open').layer(Layer.OPEN)
  FILLED = Oyster('Filled').layer(Layer.LOOSE_ROCK)
  HARD_ROCK = Oyster('Hard Rock').layer(Layer.HARD_ROCK)