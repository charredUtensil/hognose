from .position import Position

SCALE =  300

NORTH =    0
EAST  =   90
SOUTH = -180
WEST  =  -90


class Type(object):

  def __init__(self, export_id):
    self.export_id = export_id

class Building(object):

  TOOL_STORE = Type('BuildingToolStore_C')
  TELEPORT_PAD = Type('BuildingTeleportPad_C')
  SUPPORT_STATION = Type('BuildingSupportStation_C')

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