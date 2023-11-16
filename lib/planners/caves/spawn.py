import collections
import itertools
import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Building, Position, Tile
from lib.utils.geometry import adjacent

class SpawnCavePlanner(BaseCavePlanner):
  
  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = max(
        stem.suggested_crystal_count(conquest),
        math.floor(self.rng['conquest.expected_crystals'].beta(min = 2, max = 7)))

  def fine_recharge_seam(self, diorama):
    self.place_recharge_seam(diorama)

  def fine_landslides(self, diorama):
    if self.pearl_radius > 5:
      super().fine_landslides(diorama)

  def fine_buildings(self, diorama):
    for (a, b) in itertools.pairwise(self.pearl):
      x1, y1 = a.pos
      x2, y2 = b.pos
      if diorama.tiles.get((x2, y2)) == Tile.FLOOR and adjacent((x1, y1), (x2, y2)):
        self._place_toolstore(diorama, (x2, y2), (x1, y1))
        break
    else:
      x, y = self.pearl[0].pos
      self._place_toolstore(diorama, (x, y), (x, y + 1))

  def _place_toolstore(self, diorama, a, b):
    diorama.tiles[a] = Tile.FOUNDATION
    diorama.tiles[b] = Tile.FOUNDATION
    xa, ya = a
    xb, yb = b
    if ya > yb:
      facing = Position.FACING_NORTH
    elif ya < yb:
      facing = Position.FACING_SOUTH
    elif xa > xb:
      facing = Position.FACING_WEST
    else:
      facing = Position.FACING_EAST
    diorama.buildings.append(Building.at_tile(Building.Type.TOOL_STORE, a, facing))
    diorama.open_cave_flags.add(a)
    diorama.camera_origin = a

def bids(stem, conquest):
  yield (1, lambda: SpawnCavePlanner(stem, conquest, Oysters.OPEN))
  yield (1, lambda: SpawnCavePlanner(stem, conquest, Oysters.EMPTY))

class Oysters:
  OPEN = (
    Oyster('Open')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=2)
      .layer(Layer.AT_MOST_LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )
  EMPTY = (
    Oyster('Empty')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=2)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.AT_MOST_HARD_ROCK)
  )