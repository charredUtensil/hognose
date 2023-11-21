from typing import Iterable, Literal, Tuple

import enum

from .entities import Entity
from .position import Facing, Position

from lib.utils import geometry

F_DEFAULT          = ((0, 0), (0, -1))
F_CANTEEN_REFINERY = ((0, 0), (0, -1), (0, 1))
F_POWER_STATION    = ((0, 0), (0, -1), (1, 0))

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
        foundation_offsets: Tuple[Tuple[int, int]]):
      self.export_id = export_id
      self.inspect_abbrev = inspect_abbrev
      self.foundation_offsets = foundation_offsets

    TOOL_STORE = ('BuildingToolStore_C', 'TS', F_DEFAULT)
    TELEPORT_PAD = ('BuildingTeleportPad_C', 'TP', F_DEFAULT)
    CANTEEN = ('BuildingCanteen_C', 'CN', F_CANTEEN_REFINERY)
    POWER_STATION = ('BuildingPowerStation_C', 'PS', F_POWER_STATION)
    SUPPORT_STATION = ('BuildingSupportStation_C', 'SS', F_DEFAULT)

  def __init__(
      self,
      type: 'Building.Type',
      position: Position,
      foundation_tiles: Iterable[Tuple[int, int]]):
    super().__init__(position)
    self.type = type
    self.foundation_tiles = tuple(foundation_tiles)

  def serialize(self, offset: Tuple[int, int]):
    return f'{self.type.export_id},{self.position.serialize(offset)}'

  @classmethod
  def at_tile(
      cls,
      type: 'Building.Type',
      pos: Tuple[int, int],
      facing: Facing) -> 'Building':
    position = Position.at_center_of_tile(pos, facing)
    rotate = ROTATION_BY_FACING[facing]
    foundation_tiles = (
        geometry.offset(pos, rotate(ox, oy))
        for ox, oy in type.foundation_offsets)
    return cls(type, position, foundation_tiles)
    
