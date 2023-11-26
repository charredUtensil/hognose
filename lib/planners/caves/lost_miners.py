import math

from .base import BaseCavePlanner
from lib.base import Biome
from lib.planners.base import Oyster, Layer
from lib.plastic import FindMinerObjective, Position, Tile

class LostMinersCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = stem.suggested_crystal_count(conquest)
    self._miners = []

  def fine_place_entities(self, diorama):
    rng = self.rng['fine.place_entities']
    pos = self.pearl[0].pos
    diorama.tiles[pos] = Tile.FLOOR
    miners_count = math.floor(rng.beta(a = 1, b = 2, min = 1, max = 5))
    for _ in range(miners_count):
      self._miners.append(diorama.miner(
        Position.randomly_in_tile(rng, pos)))
  
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