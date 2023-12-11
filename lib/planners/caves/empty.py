import math

from .base import BaseCavePlanner
from .monster_spawners import MonsterSpawner
from lib.planners.base import Oyster, Layer
from lib.plastic import Creature, Tile

class EmptyCavePlanner(BaseCavePlanner):

  def _get_monster_spawner(self):
    creature_type = Creature.Type.monster_for_biome(self.context.biome)
    spawner = MonsterSpawner.normal(
        self,
        creature_type,
        self._stem.monster_spawn_rate)
    return spawner

def bids(stem, conquest):
  pr = stem.pearl_radius
  if stem.fluid_type == Tile.WATER:
    if pr < 10:
      yield (1, lambda: EmptyCavePlanner(
          stem, Oysters.LAKE))
    if pr > 7:
      yield (2, lambda: EmptyCavePlanner(
          stem, Oysters.ISLAND))
      if not any(p.fluid_type for p in conquest.intersecting(stem)):
        yield (1, lambda: EmptyCavePlanner(
            stem, Oysters.PENINSULA))
  elif stem.fluid_type == Tile.LAVA:
    if pr < 10:
      yield (0.5, lambda: EmptyCavePlanner(
          stem, Oysters.LAVA_LAKE))
    if pr > 7:
      yield (1, lambda: EmptyCavePlanner(
          stem, Oysters.LAVA_ISLAND))
      if not any(p.fluid_type for p in conquest.intersecting(stem)):
        yield (1, lambda: EmptyCavePlanner(
            stem, Oysters.LAVA_PENINSULA))
  else:
    if pr < 5:
      yield (0.04, lambda: EmptyCavePlanner(stem, Oysters.FILLED))
    if pr < 10:
      yield (1, lambda: EmptyCavePlanner(stem, Oysters.OPEN))
      yield (1, lambda: EmptyCavePlanner(stem, Oysters.EMPTY))
    if pr > 5:
      yield (1, lambda: EmptyCavePlanner(stem, Oysters.DOUGHNUT))

class Oysters:
  OPEN = (
    Oyster('Open')
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.AT_MOST_DIRT, width=0, grow=0.5)
      .layer(Layer.AT_MOST_LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK, grow=0.25)
  )
  EMPTY = (
    Oyster('Empty')
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.DIRT, width=0, grow=0.1)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.LOOSE_OR_HARD_ROCK, grow=0.5)
  )
  FILLED = (
    Oyster('Filled')
      .layer(Layer.DIRT, width=0, grow=0.25)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.LOOSE_OR_HARD_ROCK)
  )
  DOUGHNUT = (
    Oyster('Doughnut')
      .layer(Layer.ALWAYS_SOLID_ROCK, grow=0.2)
      .layer(Layer.ALWAYS_HARD_ROCK, grow=0.3)
      .layer(Layer.LOOSE_ROCK, width=0, grow=0.5)
      .layer(Layer.FLOOR, width=2, grow=1)
      .layer(Layer.DIRT, width=0, grow=0.5)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )
  LAKE = (
    Oyster('Lake')
      .layer(Layer.WATER, grow=2)
      .layer(Layer.FLOOR, shrink=1, grow=1)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )
  ISLAND = (
    Oyster('Island')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=0.7)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, width=0, grow=0.2)
      .layer(Layer.ALWAYS_DIRT, width=0, grow=0.5)
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=0.1)
      .layer(Layer.WATER, grow=2)
      .layer(Layer.FLOOR, grow=1)
      .layer(Layer.LOOSE_ROCK)
      .layer(Layer.AT_MOST_HARD_ROCK)
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
  LAVA_LAKE = (
    Oyster('Lava Lake')
      .layer(Layer.LAVA, grow=2)
      .layer(Layer.FLOOR, grow=1)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.AT_MOST_HARD_ROCK)
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