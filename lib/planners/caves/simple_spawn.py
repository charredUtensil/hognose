import collections
import copy
import itertools
import math

from lib.planners.caves.base import BaseCavePlanner
from lib.planners.caves.monster_spawners import MonsterSpawner
from lib.planners.base import Oyster, Layer
from lib.plastic import Building, Creature, Facing, Position, Tile
from lib.utils.geometry import adjacent


class SimpleSpawnCavePlanner(BaseCavePlanner):

  def __init__(self, stem, oyster, min_crystals):
    super().__init__(stem, oyster),
    self.min_crystals = min_crystals

  @property
  def inspect_color(self):
    return (0x00, 0xff, 0xff)

  def _get_expected_crystals(self):
    return max(
        super()._get_expected_crystals(),
        self.min_crystals,
        self.rng['conquest.expected_crystals'].beta_int(min=2, max=7))

  def _get_monster_spawner(self):
    spawner = super()._get_monster_spawner()
    spawner.min_initial_cooldown = 60
    spawner.max_initial_cooldown = 180
    return spawner

  def fine_recharge_seam(self, diorama):
    self.place_recharge_seam(diorama)

  def fine_landslides(self, diorama):
    if self.pearl_radius > 5:
      super().fine_landslides(diorama)

  def fine_buildings(self, diorama):
    for (a, b) in itertools.pairwise(self.pearl.inner):
      x1, y1 = a.pos
      x2, y2 = b.pos
      if (diorama.tiles.get((x2, y2)) == Tile.FLOOR and
          adjacent((x1, y1), (x2, y2))):
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
      facing = Facing.NORTH
    elif ya < yb:
      facing = Facing.SOUTH
    elif xa > xb:
      facing = Facing.WEST
    else:
      facing = Facing.EAST
    tool_store = Building.at_tile(
        Building.Type.TOOL_STORE, a, facing, teleport_at_start=True)
    diorama.buildings.append(tool_store)
    diorama.open_cave_flags.add(a)
    diorama.camera_position = camera_position = copy.copy(tool_store.position)
    diorama.camera_position.rp = math.pi / 4
    diorama.camera_position.ry += math.pi * 0.75


def bids(stem, conquest):
  if stem.fluid_type is None:
    if any(p.fluid_type is None for p in conquest.intersecting(stem)):
      yield (1, lambda: SimpleSpawnCavePlanner(stem, Oysters.OPEN, 0))
      yield (1, lambda: SimpleSpawnCavePlanner(stem, Oysters.EMPTY, 0))
    else:
      yield (0.1, lambda: SimpleSpawnCavePlanner(stem, Oysters.OPEN, 9))


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
