import itertools
import math

from .base import BaseCavePlanner
from lib.planners.base import Oyster, Layer
from lib.plastic import Building, Position, Tile
from lib.utils.geometry import adjacent

CAN_BE_IN_FRONT_OF_RECHARGE_SEAM = frozenset((
    Tile.FLOOR,
    Tile.DIRT,
    Tile.LOOSE_ROCK,
    Tile.HARD_ROCK,
    Tile.CRYSTAL_SEAM,
    Tile.ORE_SEAM))

class SpawnCavePlanner(BaseCavePlanner):
  
  def __init__(self, stem, conquest, oyster):
    super().__init__(stem, oyster)
    self.expected_crystals = max(0, math.floor(self.rng.normal(mean=5, stddev=1)))

  def fine(self, diorama):
    super().fine(diorama)
    for ((x1, y1), _, _), ((x2, y2), _, _) in itertools.pairwise(self.pearl):
      if diorama.tiles.get((x2, y2)) == Tile.FLOOR and adjacent((x1, y1), (x2, y2)):
        self._place_toolstore(diorama, (x2, y2), (x1, y1))
        break
    else:
      x, y = self.pearl[0].pos
      self._place_toolstore(diorama, (x, y), (x, y + 1))
    self._place_recharge_seam(diorama)

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
      facing = Position.FACING_EAST
    else:
      facing = Position.FACING_WEST
    diorama.buildings.append(Building(Building.TOOL_STORE, a, facing))
    diorama.open_cave_flags.add(a)
    diorama.camera_origin = a

  def _place_recharge_seam(self, diorama):
    last_layer = self.pearl[-1].layer
    def placements():
      for (x, y), layer, _ in self.pearl:
        if layer < last_layer:
          pass
        elif diorama.tiles.get((x, y)) not in CAN_BE_IN_FRONT_OF_RECHARGE_SEAM:
          pass
        else:
          for (ox, oy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            if diorama.tiles.get((x + ox, y + oy), Tile.SOLID_ROCK) == Tile.SOLID_ROCK:
              value = sum(
                1 for (ox2, oy2)
                in ((0, -1), (0, 1), (-1, 0), (1, 0))
                if diorama.tiles.get(
                    (x + ox + ox2, y + oy + oy2),
                    Tile.SOLID_ROCK) == Tile.SOLID_ROCK)
              yield (value, (x + ox, y + oy))
    _, (x, y) = max(placements())
    diorama.tiles[x, y] = Tile.RECHARGE_SEAM

  @classmethod
  def bids(cls, stem, conquest):
    yield (1, lambda: cls(stem, conquest, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster('Default')
      .layer(Layer.FLOOR, width=2, grow=2)
      .layer(Layer.LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK)
  )