from typing import Iterable, Literal, Tuple

import copy
import enum
import itertools
import math

from .entities import Entity
from .position import Facing, Position

from lib.utils import geometry

# There are five unique "footprints" for buildings available.
# Assuming the building itself has its entity origin at (0, 0), and is facing
# NORTH, these tiles become the foundation tiles for buildings with that
# footprint.
F_MINING_LASER     = ((0, 0),                           )
F_DEFAULT          = ((0, 0),                    (0, -1))
F_CANTEEN_REFINERY = ((0, 0), (0, 1),            (0, -1))
F_POWER_STATION    = ((0, 0), (1, 0),            (0, -1))
F_SUPER_TELEPORT   = ((0, 0), (-1, -1), (-1, 0), (0, -1))

ROTATION_BY_FACING = {
    Facing.NORTH : lambda x, y: (x, y),
    Facing.EAST  : geometry.rotate_right,
    Facing.SOUTH : geometry.rotate_180,
    Facing.WEST  : geometry.rotate_left,
}

class BuildingDoesNotFitException(Exception):
  pass

class Building(Entity):
  
  class Type(enum.Enum):

    def __init__(
        self,
        export_id: str,
        inspect_abbrev: str,
        max_level: int,
        crystals: int,
        foundation_offsets: Tuple[Tuple[int, int]]):
      self.export_id = export_id
      self.inspect_abbrev = inspect_abbrev
      self.max_level = max_level
      self.crystals = crystals
      self.foundation_offsets = foundation_offsets

    TOOL_STORE = ('BuildingToolStore_C', 'E', 3, 0, F_DEFAULT)
    TELEPORT_PAD = ('BuildingTeleportPad_C', 'T', 2, 0, F_DEFAULT)
    # Docs faces the LAND tile with the water BEHIND it.
    # Note the water tile is not counted as part of the foundation
    DOCKS = ('BuildingDocks_C', 'D', 1, 1, F_DEFAULT)
    # The canteen is functionally symmetrical, but if you care, the end with
    # the yellow/black chevron piece is the FRONT.
    CANTEEN = ('BuildingCanteen_C', 'C', 1, 1, F_CANTEEN_REFINERY)
    # Power Station origin is the RIGHT side of the building where miners put
    # the crystals in.
    POWER_STATION = ('BuildingPowerStation_C', 'P', 2, 2, F_POWER_STATION)
    SUPPORT_STATION = ('BuildingSupportStation_C', 'S', 2, 3, F_DEFAULT)
    UPGRADE_STATION = ('BuildingUpgradeStation_C', 'U', 3, 3, F_DEFAULT)
    # Geological Center origin is the BACK of the building.
    GEOLOGICAL_CENTER = ('BuildingGeologicalCenter_C', 'G', 5, 2, F_DEFAULT)
    # Ore Refinery origin is the FRONT of the building were miners put ore in.
    ORE_REFINERY = ('BuildingOreRefinery_C', 'R', 4, 3, F_CANTEEN_REFINERY)
    MINING_LASER = ('BuildingMiningLaser_C', 'L', 1, 1, F_MINING_LASER)
    # Super teleport origin is the LEFT side of the building when facing it.
    SUPER_TELEPORT = ('BuildingSuperTeleport_C', 'X', 2, 4, F_SUPER_TELEPORT)

  def __init__(
      self,
      type: 'Building.Type',
      position: Position,
      foundation_tiles: Iterable[Tuple[int, int]],
      level: int = 1,
      essential: bool = False,
      teleport_at_start: bool = False):
    super().__init__(position)
    self.type = type
    self.foundation_tiles = tuple(foundation_tiles)
    self.level = level
    self.essential = essential
    self.teleport_at_start = teleport_at_start

  def serialize(self, offset: Tuple[int, int]):
    position = copy.copy(self.position)
    position.ry += math.pi / 2
    return (
        f'{self.type.export_id},'
        f'{position.serialize(offset)}'
        f'{f",Level={self.level:d}" if self.level > 1 else ""}'
        f'{",Essential=True" if self.essential else ""}'
        f'{",Teleport=True" if self.teleport_at_start else ""}')

  @classmethod
  def at_tile(
      cls,
      type: 'Building.Type',
      pos: Tuple[int, int],
      facing: Facing,
      level: int = 1,
      essential: bool = False,
      teleport_at_start: bool = False) -> 'Building':
    position = Position.at_center_of_tile(pos, facing)
    rotate = ROTATION_BY_FACING[facing]
    foundation_tiles = (
        geometry.offset(pos, rotate(ox, oy))
        for ox, oy in type.foundation_offsets)
    return cls(
        type, position, foundation_tiles, level, essential, teleport_at_start)

  @classmethod
  def fit_in_bounds(
      cls,
      type: 'Building.type',
      bounds: Tuple[int, int, int, int],
      first_facing: Facing,
      level: int = 1,
      essential: bool = False,
      teleport_at_start: bool = False) -> 'Building':
    bl, bt, br, bb = bounds
    bw = br - bl
    bh = bb - bt
    flu, flv, fou, fov = _bound_foundation(type)
    
    rotation_index = {
        Facing.NORTH: 0,
        Facing.EAST: 1,
        Facing.SOUTH: 2,
        Facing.WEST: 3,
    }[first_facing]
    rotations = (
        (Facing.NORTH, flu, flv,           fou,           fov),
        (Facing.EAST,  flv, flu, flv - 1 - fov,           fou),
        (Facing.SOUTH, flu, flv, flu - 1 - fou, flv - 1 - fov),
        (Facing.WEST,  flv, flu,           fov, flu - 1 - fou),
    )
    for facing, fw, fh, fox, foy in itertools.islice(
        itertools.cycle(rotations), rotation_index, rotation_index + 4):
      if fw > bw or fh > bh:
        continue
      return cls.at_tile(
          type,
          (bl + fox, bt + foy),
          facing,
          level,
          essential,
          teleport_at_start)
    raise BuildingDoesNotFitException(
      f'{type} with bounds {flu}x{flv} does not fit in area of {bw}x{bh}')

def _bound_foundation(type: 'Building.Type') -> Tuple[int, int, int, int]:
  l = min(x for x, _ in type.foundation_offsets)
  r = max(x for x, _ in type.foundation_offsets) + 1
  t = min(y for _, y in type.foundation_offsets)
  b = max(y for _, y in type.foundation_offsets) + 1
  return (r - l, b - t, -l, -t)
