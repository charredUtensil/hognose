from typing import Iterable, Literal, Tuple

import copy
import enum
import math

from .entities import Entity
from .position import Facing, Position

from lib.utils import geometry

F_MINING_LASER     = ((0, 0),)
F_DEFAULT          = ((0, 0), (0, -1))
F_CANTEEN_REFINERY = ((0, 0), (0, -1), (0, 1))
F_POWER_STATION    = ((0, 0), (0, -1), (1, 0))
F_SUPER_TELEPORT   = ((0, 0), (0, -1), (-1, -1), (-1, 0))

ROTATION_BY_FACING = {
    Facing.NORTH : lambda x, y: (x, y),
    Facing.EAST  : geometry.rotate_right,
    Facing.SOUTH : geometry.rotate_180,
    Facing.WEST  : geometry.rotate_left,
}

class Building(Entity):
  
  class Type(enum.Enum):

    def __init__(
        self,
        export_id: str,
        inspect_abbrev: str,
        max_level: int,
        foundation_offsets: Tuple[Tuple[int, int]]):
      self.export_id = export_id
      self.inspect_abbrev = inspect_abbrev
      self.max_level = max_level
      self.foundation_offsets = foundation_offsets

    TOOL_STORE = ('BuildingToolStore_C', 'TS', 3, F_DEFAULT)
    TELEPORT_PAD = ('BuildingTeleportPad_C', 'TP', 2, F_DEFAULT)
    # Docs faces the LAND tile with the water BEHIND it.
    DOCKS = ('BuildingDocks_C', 'DK', 1, F_DEFAULT)
    # The canteen is functionally symmetrical, but if you care, the end with
    # the yellow/black chevron piece is the FRONT.
    CANTEEN = ('BuildingCanteen_C', 'CN', 1, F_CANTEEN_REFINERY)
    # Power Station origin is the RIGHT side of the building where miners put
    # the crystals in.
    POWER_STATION = ('BuildingPowerStation_C', 'PS', 2, F_POWER_STATION)
    SUPPORT_STATION = ('BuildingSupportStation_C', 'SS', 2, F_DEFAULT)
    UPGRADE_STATION = ('BuildingUpgradeStation_C', 'US', 3, F_DEFAULT)
    # Geological Center origin is the BACK of the building.
    GEOLOGICAL_CENTER = ('BuildingGeologicalCenter_C', 'GC', 5, F_DEFAULT)
    # Ore Refinery origin is the FRONT of the building were miners put ore in.
    ORE_REFINERY = ('BuildingOreRefinery_C', 'OR', 4, F_CANTEEN_REFINERY)
    MINING_LASER = ('BuildingMiningLaser_C', 'ML', 1, F_MINING_LASER)
    # Super teleport origin is the LEFT side of the building when facing it.
    SUPER_TELEPORT = ('BuildingSuperTeleport_C', 'ST', 2, F_SUPER_TELEPORT)

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
    
