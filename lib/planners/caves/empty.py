import math

from .base import BaseCavePlanner
from .monster_spawners import MonsterSpawner
from lib.planners.base import Oyster, Layer
from lib.plastic import Creature, Tile

class EmptyCavePlanner(BaseCavePlanner):
  @property
  def inspect_color(self):
    return (0xff, 0xff, 0xff)
    
def bids(stem, conquest):
  if stem.fluid_type is None:
    pr = stem.pearl_radius
    if pr < 4:
      yield (0.04, lambda: EmptyCavePlanner(stem, Oysters.FILLED))
    if pr < 10:
      yield (2, lambda: EmptyCavePlanner(stem, Oysters.OPEN))
      yield (1, lambda: EmptyCavePlanner(stem, Oysters.EMPTY))
    if pr > 5:
      yield (0.5, lambda: EmptyCavePlanner(stem, Oysters.DOUGHNUT))

class Oysters:
  OPEN = (
    Oyster('Open')
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.AT_MOST_DIRT, width=0, grow=0.5)
      .layer(Layer.AT_MOST_LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK, grow=0.25)
      .layer(Layer.VOID, width=0, grow=0.5)
  )
  EMPTY = (
    Oyster('Empty')
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.DIRT, width=0, grow=0.1)
      .layer(Layer.DIRT_OR_LOOSE_ROCK, grow=1)
      .layer(Layer.LOOSE_OR_HARD_ROCK, grow=0.5)
      .layer(Layer.VOID, width=0, grow=0.5)
  )
  FILLED = (
    Oyster('Filled')
      .layer(Layer.DIRT, width=0, grow=0.25)
      .layer(Layer.DIRT_OR_LOOSE_ROCK, grow=1)
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