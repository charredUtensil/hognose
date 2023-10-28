import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class TreasureCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem)
    self.oyster = oyster
    self.expected_crystals = math.floor(
      conquest.expected_crystals * self.rng.normal(0.4, 0.1))

  def fine(self, canvas):
    cx, cy = self.rng.choice(self.baseplates).center
    for _ in range(self.expected_crystals):
      x, y = self.rng.point_in_circle(2, (cx, cy))
      x = math.floor(x)
      y = math.floor(y)
      canvas.crystals[x, y] += 1

  @classmethod
  def bids(cls, stem, conquest):
    if len(conquest.intersecting(stem)) <= 2:
      yield (1, lambda: cls(stem, conquest, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster()
      .layer(Layer.FLOOR, width=2, grow=2)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK)
  )