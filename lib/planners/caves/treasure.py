from typing import Tuple

import itertools
import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Tile

class TreasureCavePlanner(BaseCavePlanner):

  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = math.floor(
      stem.suggested_crystal_count(conquest)
      * (1 + abs(self.rng['conquest.expected_crystals'].normal(0, 3))))

  def fine_crystals(self, diorama):
    self.place_crystals(diorama, math.floor(self.expected_crystals * 0.2))
    places = tuple(pos for pos, layer, _ in self.pearl if layer == 0)
    for x, y in itertools.islice(
        itertools.cycle(places), math.ceil(self.expected_crystals * 0.8)):
      diorama.crystals[x, y] += 1

  @classmethod
  def bids(cls, stem, conquest):
    if len(conquest.intersecting(stem)) > 2:
      # Only put treasure caves at dead ends
      return
    pr = stem.pearl_radius
    if stem.fluid_type == Tile.WATER and pr > 4:
      yield (0.5, lambda: cls(stem, conquest, Oysters.ISLAND_HOARD))
      yield (0.5, lambda: cls(stem, conquest, Oysters.PENINSULA_HOARD))
    elif stem.fluid_type == Tile.LAVA and pr > 4:
      yield (0.5, lambda: cls(stem, conquest, Oysters.LAVA_ISLAND_HOARD))
      yield (0.5, lambda: cls(stem, conquest, Oysters.LAVA_PENINSULA_HOARD))
    else:
      yield (1, lambda: cls(stem, conquest, Oysters.OPEN_HOARD))

class Oysters:
  OPEN_HOARD = (
    Oyster('Open Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  ISLAND_HOARD = (
    Oyster('Island Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=1)
      .layer(Layer.WATER, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  PENINSULA_HOARD = (
    Oyster('Peninsula Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=1)
      .layer(Layer.BRIDGE_ON_WATER, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  LAVA_ISLAND_HOARD = (
    Oyster('Lava Island Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=1)
      .layer(Layer.LAVA, width=2, grow=3)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  LAVA_PENINSULA_HOARD = (
    Oyster('Lava Peninsula Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=1)
      .layer(Layer.BRIDGE_ON_LAVA, width=2, grow=3)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )