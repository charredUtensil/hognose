from typing import Tuple

from .position import Position

NORTH =    0
EAST  =   90
SOUTH = -180
WEST  =  -90


class Type(object):

  def __init__(self, export_id, inspect_abbrev):
    self.export_id = export_id
    self.inspect_abbrev = inspect_abbrev

class Building(object):

  TOOL_STORE = Type('BuildingToolStore_C', 'TS')
  TELEPORT_PAD = Type('BuildingTeleportPad_C', 'TP')
  SUPPORT_STATION = Type('BuildingSupportStation_C', 'SS')

  def __init__(self, type: Type, pos: Tuple[int, int], facing):
    self.type = type
    self.x, self.y = pos
    self.facing = facing

  def serialize(self, offset: Tuple[int, int]):
    position = Position(
      (self.x + 0.5, self.y + 0.5, 0),
      (0, self.facing, 0)
    )
    return (
      f'{self.type.export_id},{position.serialize(offset)}'
    )