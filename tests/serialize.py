from collections.abc import Callable
from typing import Dict, Tuple, TypeVar

T = TypeVar('T')

import re
import os.path
import unittest

from lib.base import Context
from lib.plastic import Building, Creature, Diorama, Facing, Miner, Position, Tile

RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')
SANITIZE_RE = re.compile(r'^comments{$.*?^}$', re.DOTALL | re.MULTILINE)

def sanitize(data: str) -> str:
  return SANITIZE_RE.sub('comments{\n[REDACTED]\n}', data)

def fill(
    t: Dict[Tuple[int, int], T],
    left: int,
    top: int,
    width: int, 
    height: int,
    value: T):
  for x in range(left, left + width):
    for y in range(top, top + height):
      t[x, y] = value

def mvp() -> Diorama:
  d = Diorama(Context('0', None))

  fill(d.crystals, 0, -3, 3, 3, 3)
  fill(d.tiles,    0, -2, 3, 1, Tile.HARD_ROCK)
  fill(d.tiles,    0, -2, 3, 1, Tile.LOOSE_ROCK)
  fill(d.tiles,    0, -1, 3, 1, Tile.DIRT)
  fill(d.tiles,    0,  0, 3, 2, Tile.FLOOR)
  d.tiles[2, 1] = Tile.POWER_PATH

  origin = (0, 1)
  tool_store = Building.at_tile(
      Building.Type.TOOL_STORE, origin, Facing.EAST)
  d.buildings.append(tool_store)
  d.open_cave_flags.add(origin)
  d.camera_origin = origin
  for pos in tool_store.foundation_tiles:
    d.tiles[pos] = Tile.FOUNDATION
  
  d.discover()
  d.bounds = (-2, -4, 7, 7)
  return d

def building_zoo() -> Diorama:
  d = Diorama(Context('0', None))
  d.open_cave_flags.add((0, 0))
  d.camera_origin = (0, 0)
  size = 12
  fill(d.tiles, 0, 0, size, size, Tile.FLOOR)
  d.discover()
  d.bounds = (-1, -1, size + 2, size + 2)

  def b(t, origin, facing):
    b = Building.at_tile(t, origin, facing)
    for pos in b.foundation_tiles:
      d.tiles[pos] = Tile.FOUNDATION
    d.buildings.append(b)
  
  b(Building.Type.TOOL_STORE, (2, 0), Facing.SOUTH)
  b(Building.Type.TOOL_STORE, (0, 2), Facing.EAST)
  b(Building.Type.TOOL_STORE, (4, 2), Facing.WEST)
  b(Building.Type.TOOL_STORE, (2, 4), Facing.NORTH)

  b(Building.Type.TELEPORT_PAD, (6, 0), Facing.SOUTH)
  b(Building.Type.SUPPORT_STATION, (8, 0), Facing.SOUTH)

  b(Building.Type.CANTEEN, (7, 3), Facing.WEST)

  b(Building.Type.POWER_STATION, (11, 0), Facing.SOUTH)
  b(Building.Type.POWER_STATION, (10, 3), Facing.NORTH)
  b(Building.Type.POWER_STATION, (0, 5), Facing.EAST)
  b(Building.Type.POWER_STATION, (3, 6), Facing.WEST)

  return d

def entity_zoo() -> Diorama:
  d = Diorama(Context('0', None))
  d.open_cave_flags.add((0, 0))
  d.camera_origin = (0, 0)
  size = 12
  fill(d.tiles, 0, 0, size, size, Tile.FLOOR)
  d.discover()
  d.bounds = (-1, -1, size + 2, size + 2)

  miners_facing = (1.5, 1.5)
  d.miner(Position.at_center_of_tile((0, 0), facing=miners_facing))
  d.miner(Position.at_center_of_tile((1, 0), facing=miners_facing), level=2)
  d.miner(Position.at_center_of_tile((2, 0), facing=miners_facing), level=3)
  d.miner(Position.at_center_of_tile((3, 0), facing=miners_facing), level=4)
  d.miner(Position.at_center_of_tile((4, 0), facing=miners_facing), level=5)
  d.miner(Position.at_center_of_tile((0, 1), facing=miners_facing), essential=True)
  d.miner(
      Position.at_center_of_tile((2, 1), facing=miners_facing),
      unique=Miner.Unique.OFFICER)
  d.miner(
      Position.at_center_of_tile((3, 1), facing=miners_facing),
      unique=Miner.Unique.CHIEF)
  d.miner(
      Position.at_center_of_tile((0, 2), facing=miners_facing),
      unique=Miner.Unique.AXLE,
      loadout=[Miner.Loadout.DRILL, Miner.Loadout.JOB_DRIVER])
  d.miner(
      Position.at_center_of_tile((1, 2), facing=miners_facing),
      unique=Miner.Unique.BANDIT,
      loadout=[Miner.Loadout.DRILL, Miner.Loadout.JOB_SAILOR])
  d.miner(
      Position.at_center_of_tile((2, 2), facing=miners_facing),
      unique=Miner.Unique.DOCS,
      loadout=[Miner.Loadout.DRILL, Miner.Loadout.JOB_GEOLOGIST])
  d.miner(
      Position.at_center_of_tile((3, 2), facing=miners_facing),
      unique=Miner.Unique.JET,
      loadout=[Miner.Loadout.DRILL, Miner.Loadout.JOB_PILOT])
  d.miner(
      Position.at_center_of_tile((4, 2), facing=miners_facing),
      unique=Miner.Unique.SPARKS,
      loadout=[Miner.Loadout.DRILL, Miner.Loadout.JOB_ENGINEER])

  d.creature(
    Creature.Type.ROCK_MONSTER,
    Position.at_center_of_tile((5, 0), Facing.SOUTH))
  d.creature(
    Creature.Type.ICE_MONSTER,
    Position.at_center_of_tile((6, 0), Facing.SOUTH))
  d.creature(
    Creature.Type.LAVA_MONSTER,
    Position.at_center_of_tile((7, 0), Facing.SOUTH))

  d.creature(
    Creature.Type.ROCK_MONSTER,
    Position.at_center_of_tile((5, 3), Facing.NORTH), sleep=True)
  d.creature(
    Creature.Type.ICE_MONSTER,
    Position.at_center_of_tile((6, 3), Facing.NORTH), sleep=True)
  d.creature(
    Creature.Type.LAVA_MONSTER,
    Position.at_center_of_tile((7, 3), Facing.NORTH), sleep=True)

  d.creature(
    Creature.Type.SLIMY_SLUG,
    Position.at_center_of_tile((0, 3), Facing.EAST))
  d.creature(
    Creature.Type.SLIMY_SLUG,
    Position.at_center_of_tile((1, 3), Facing.WEST), sleep=True)

  d.creature(
    Creature.Type.SMALL_SPIDER,
    Position.at_center_of_tile((3, 3), Facing.NORTH))

  d.creature(
    Creature.Type.BAT,
    Position.at_center_of_tile((0, 5), Facing.NORTH))

  return d

TESTS = (
  ('mvp', mvp),
  ('building_zoo', building_zoo),
  ('entity_zoo', entity_zoo),
)

class TestSerialize(unittest.TestCase):

  def _do(self, name: str, fn: Callable[[], Diorama]):
    data = sanitize(fn().serialize())
    with open(os.path.join(RESOURCE_DIR, f'{name}.dat')) as f:
      self.assertEqual(data, f.read())
  
for name, fn in TESTS:
  def test(self):
    self._do(name, fn)
  setattr(TestSerialize, f'test_{name}', test)

def update_resources():
  for name, fn in TESTS:
    data = sanitize(fn().serialize())
    with open(os.path.join(RESOURCE_DIR, f'{name}.dat'), 'w') as f:
      f.write(data)