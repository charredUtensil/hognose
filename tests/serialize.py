from typing import Dict, Tuple, TypeVar

from lib.plastic import (
    Building, Creature, Diorama, Facing, Miner, Position, Tile)
from lib.base import Context
from tests.base import SerializedCavernTest

T = TypeVar('T')


def fill(
        t: Dict[Tuple[int, int], T],
        left: int,
        top: int,
        width: int,
        height: int,
        value: T):
  """Fills the given rectangle in t with the given value."""
  for x in range(left, left + width):
    for y in range(top, top + height):
      t[x, y] = value

class TestSerialize(SerializedCavernTest):
  """Tests that some handcrafted Dioramas serialize to the correct strings."""
  # pylint: disable=missing-function-docstring,invalid-name

  def test_serializesDiorama_mvp(self):
    d = Diorama(Context('0', None))

    fill(d.crystals, 0, -3, 3, 3, 3)
    fill(d.tiles, 0, -2, 3, 1, Tile.HARD_ROCK)
    fill(d.tiles, 0, -2, 3, 1, Tile.LOOSE_ROCK)
    fill(d.tiles, 0, -1, 3, 1, Tile.DIRT)
    fill(d.tiles, 0, 0, 3, 2, Tile.FLOOR)
    d.tiles[2, 1] = Tile.POWER_PATH

    origin = (0, 1)
    tool_store = Building.at_tile(
        Building.Type.TOOL_STORE, origin, Facing.EAST)
    d.buildings.append(tool_store)
    d.open_cave_flags.add(origin)
    for pos in tool_store.foundation_tiles:
      d.tiles[pos] = Tile.FOUNDATION

    d.discover()
    d.bounds = (-2, -4, 7, 7)

    self.assertDioramaMatches(d, 'serialize/mvp')

  def test_serializesDiorama_buildingZoo(self):
    d = Diorama(Context('0', None))
    d.open_cave_flags.add((0, 0))
    size = 12
    fill(d.tiles, 0, 0, size, size, Tile.FLOOR)
    d.discover()
    d.bounds = (-1, -1, size + 2, size + 2)

    def b(*args, **kwargs):
      b = Building.at_tile(*args, **kwargs)
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

    d.tiles[5, 6] = Tile.WATER
    b(Building.Type.DOCKS, (5, 5), Facing.NORTH)
    b(Building.Type.UPGRADE_STATION, (7, 5), Facing.SOUTH)
    b(Building.Type.GEOLOGICAL_CENTER, (9, 5), Facing.SOUTH)
    b(Building.Type.MINING_LASER, (11, 5), Facing.SOUTH)

    b(Building.Type.ORE_REFINERY, (1, 8), Facing.EAST)
    b(Building.Type.SUPER_TELEPORT, (5, 8), Facing.NORTH)

    b(Building.Type.TOOL_STORE, (8, 8), Facing.NORTH, level=2)
    b(Building.Type.TOOL_STORE, (10, 8), Facing.NORTH, level=3)

    b(Building.Type.TOOL_STORE, (0, 10), Facing.SOUTH, essential=True)
    b(Building.Type.TOOL_STORE, (2, 10), Facing.SOUTH, teleport_at_start=True)
    b(Building.Type.TOOL_STORE, (4, 10), Facing.SOUTH,
      essential=True, teleport_at_start=True)
    b(Building.Type.TOOL_STORE, (6, 10), Facing.SOUTH,
      level=3, essential=True, teleport_at_start=True)

    self.assertDioramaMatches(d, 'serialize/building_zoo')

  def test_serializesDiorama_entityZoo(self):
    d = Diorama(Context('0', None))
    d.open_cave_flags.add((0, 0))
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
    d.miner(
        Position.at_center_of_tile(
            (0, 1), facing=miners_facing), essential=True)
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

    self.assertDioramaMatches(d, 'serialize/entity_zoo')
