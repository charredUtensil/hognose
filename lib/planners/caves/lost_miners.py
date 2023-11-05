from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import FindMinerObjective

class LostMinersCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = stem.suggested_crystal_count(conquest)
    self._miners = []

  def fine(self, diorama):
    super().fine(diorama)
    x, y = self.pearl[0].pos
    self._miners.append(diorama.miner(
        (x + 0.5, y + 0.5), 0))
  
  @property
  def objectives(self):
    return [FindMinerObjective(m) for m in self._miners]

  @classmethod
  def bids(cls, stem, conquest):
    if stem.fluid_type is None and conquest.remaining <= 3:
      yield (1, lambda: cls(stem, conquest, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster('Default')
      .layer(Layer.FLOOR, width=2, grow=2)
      .layer(Layer.LOOSE_ROCK, width=0, grow=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )