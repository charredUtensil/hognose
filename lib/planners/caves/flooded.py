import itertools
import math

from .base import BaseCavePlanner
from .monster_spawners import MonsterSpawner
from lib.base import Biome
from lib.planners.base import Oyster, Layer
from lib.plastic import Creature, Tile
from lib.utils.geometry import plot_line

class FloodedCavePlanner(BaseCavePlanner):
  @property
  def inspect_color(self):
    return self.fluid_type.inspect_color

  def _get_monster_spawner(self):
    if self.fluid_type == Tile.WATER and self.context.biome == Biome.LAVA:
      # Don't spawn lava monsters in a water cave
      return None
    elif self.fluid_type == Tile.LAVA and self.context.biome != Biome.LAVA:
      # Don't spawn rock or ice monsters in a lava cave
      return None
    return super()._get_monster_spawner()

class ContiguousFloodedCavePlanner(FloodedCavePlanner):
  def rough(self, tiles):
    for a, b in itertools.pairwise(self.baseplates):
      for x, y in plot_line(a.center, b.center, True):
        tiles[x, y] = self.fluid_type
    super().rough(tiles)

def bids(stem, conquest):
  pr = stem.pearl_radius
  if stem.fluid_type == Tile.WATER:
    if pr < 10:
      yield (1, lambda: ContiguousFloodedCavePlanner(
          stem, Oysters.LAKE))
    if pr > 5:
      yield (2, lambda: ContiguousFloodedCavePlanner(
          stem, Oysters.ISLAND))
      if not any(p.fluid_type for p in conquest.intersecting(stem)):
        yield (1, lambda: FloodedCavePlanner(
            stem, Oysters.PENINSULA))
  elif stem.fluid_type == Tile.LAVA:
    if pr < 10:
      yield (0.5, lambda: ContiguousFloodedCavePlanner(
          stem, Oysters.LAVA_LAKE))
    if pr > 5:
      yield (1, lambda: ContiguousFloodedCavePlanner(
          stem, Oysters.LAVA_ISLAND))
      if not any(p.fluid_type for p in conquest.intersecting(stem)):
        yield (1, lambda: FloodedCavePlanner(
            stem, Oysters.LAVA_PENINSULA))

class Oysters:
  LAKE = (
    Oyster('Lake')
      .layer(Layer.WATER, grow=2)
      .layer(Layer.FLOOR, shrink=1, grow=1)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.LOOSE_OR_HARD_ROCK)
  )
  ISLAND = (
    Oyster('Island')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=0.7)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_DIRT, grow=0.5)
      .layer(Layer.ALWAYS_FLOOR, grow=0.1)
      .layer(Layer.WATER, grow=2)
      .layer(Layer.FLOOR, grow=1)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.LOOSE_OR_HARD_ROCK)
  )
  LAVA_LAKE = (
    Oyster('Lava Lake')
      .layer(Layer.LAVA, grow=2)
      .layer(Layer.FLOOR, grow=1)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.LOOSE_OR_HARD_ROCK)
  )
  LAVA_ISLAND = (
    Oyster('Lava Island')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=0.7)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=0.1)
      .layer(Layer.LAVA, grow=2)
      .layer(Layer.FLOOR, grow=0.5)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.LOOSE_OR_HARD_ROCK)
  )
  PENINSULA = (
    Oyster('Peninsula')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=0.7)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_DIRT, width=0, grow=0.5)
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=0.1)
      .layer(Layer.BRIDGE_ON_WATER, grow=2)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )
  LAVA_PENINSULA = (
    Oyster('Lava Peninsula')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=0.7)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, grow=0.2)
      .layer(Layer.ALWAYS_FLOOR, grow=0.1)
      .layer(Layer.BRIDGE_ON_LAVA, grow=2)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )