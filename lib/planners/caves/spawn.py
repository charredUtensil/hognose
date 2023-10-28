import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Building, Tile

class SpawnCavePlanner(BaseCavePlanner):
  
  def __init__(self, stem, conquest, oyster):
    super().__init__(stem)
    self.expected_crystals = max(0, math.floor(self.rng.normal(mean=5, stddev=1)))
    self.oyster = oyster

    lot = self.rng.choice(self.baseplates)
    self._toolstore = tuple(
      math.floor(n) for n in self.rng.point_in_circle(3, lot.center))

  def fine(self, diorama):
    super().fine(diorama)
    diorama.tiles[self._toolstore] = Tile.FOUNDATION
    diorama.tiles[self._toolstore[0], self._toolstore[1] - 1] = Tile.FOUNDATION
    diorama.buildings.append(Building(Building.TOOL_STORE, self._toolstore, 0))
    diorama.open_cave_flags.add(self._toolstore)
    diorama.camera_origin = self._toolstore

  @classmethod
  def bids(cls, stem, conquest):
    yield (1, lambda: cls(stem, conquest, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster()
      .layer(Layer.FLOOR, width=2, grow=2)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK)
  )