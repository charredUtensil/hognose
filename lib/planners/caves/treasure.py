import itertools
import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class TreasureCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = math.floor(
      stem.suggested_crystal_count(conquest) * (1 + abs(self.rng.normal(0, 3))))

  def fine(self, canvas):
    places = tuple(pos for pos, layer, _ in self.pearl if layer == 0)
    for x, y in itertools.islice(itertools.cycle(places), self.expected_crystals):
      canvas.crystals[x, y] += 1

  @classmethod
  def bids(cls, stem, conquest):
    if len(conquest.intersecting(stem)) <= 2:
      yield (1, lambda: cls(stem, conquest, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster('Default')
      .layer(Layer.FLOOR, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )