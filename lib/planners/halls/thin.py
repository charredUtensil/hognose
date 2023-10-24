from .base import BaseHallPlanner
from lib.plastic import Tile

class ThinHallPlanner(BaseHallPlanner):

  def __init__(self, stem, conquest, base_layer):
    super().__init__(stem)
    self._base_layer = base_layer

  def rough(self, tiles):
    for (x, y) in self.walk_stream():
      if tiles.get((x, y)) not in (Tile.WATER, Tile.LAVA):
        tiles[x, y] = self._base_layer

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type is None:
      if conquest.expected_crystals > (0 +
          + 2     # Power Station
          + 3 + 1 # Support Station (powered)
          + 4 + 1 # Super Teleport  (powered)
          + 5     # Granite Grinder
          ):
        yield (0.4, lambda: cls(stem, conquest, Tile.HARD_ROCK))
      yield   (0.1, lambda: cls(stem, conquest, Tile.FLOOR))
      yield   (0.2, lambda: cls(stem, conquest, Tile.LOOSE_ROCK))