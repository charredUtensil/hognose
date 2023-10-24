from .position import Position

SCALE =  300

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

  def __init__(self, type, pos, facing):
    self.type = type
    self.x, self.y = pos
    self.facing = facing

  def serialize(self, offset):
    position = Position(
      (
        (self.x + 0.5) * SCALE,
        (self.y + 0.5) * SCALE,
        0
      ),
      (0, self.facing, 0)
    )
    return (
      f'{self.type.export_id},{position.serialize(offset)}'
    )