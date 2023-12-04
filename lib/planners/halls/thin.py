from .base import BaseHallPlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class ThinHallPlanner(BaseHallPlanner):
  
  @property
  def pearl_radius(self):
    return 0

def bids(stem, conquest):
  if stem.fluid_type is None:
    yield   (0.1, lambda: ThinHallPlanner(stem, Oysters.OPEN))
    yield   (0.2, lambda: ThinHallPlanner(stem, Oysters.FILLED))
    if conquest.expected_crystals > (0 +
        + 2     # Power Station
        + 3 + 1 # Support Station (powered)
        + 4 + 1 # Super Teleport  (powered)
        + 5     # Granite Grinder
        ):
      yield (0.4, lambda: ThinHallPlanner(stem, Oysters.HARD_ROCK))

class Oysters:
  OPEN = Oyster('Open').layer(Layer.FLOOR)
  FILLED = Oyster('Filled').layer(Layer.LOOSE_ROCK)
  HARD_ROCK = Oyster('Hard Rock').layer(Layer.HARD_ROCK)