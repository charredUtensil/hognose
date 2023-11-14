from .base import BaseCavePlanner
from lib.base import Biome
from lib.planners.base import Oyster, Layer
from lib.plastic import FindMinerObjective, Tile

class LostMinersCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = stem.suggested_crystal_count(conquest)
    self._miners = []

  def fine(self, diorama):
    super().fine(diorama)
    x, y = self.pearl[0].pos
    diorama.tiles[x, y] = Tile.FLOOR
    self._miners.append(diorama.miner(
        (x + 0.5, y + 0.5), 0))
  
  @property
  def objectives(self):
    return [FindMinerObjective(m) for m in self._miners]

def bids(stem, conquest):
  if stem.fluid_type is None and conquest.remaining <= 3:
    # The L.M.S. Explorer's teleporters just seem to be real lousy in ice
    # caverns for some reason.
    multiplier = {
      Biome.ROCK: 1.0,
      Biome.ICE : 1.4,
      Biome.LAVA: 0.7,
    }[stem.context.biome]
    yield (multiplier, lambda: LostMinersCavePlanner(stem, conquest, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster('Default')
      .layer(Layer.ALWAYS_FLOOR, width=2, shrink=1, grow=2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )