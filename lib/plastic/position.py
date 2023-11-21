from typing import Optional, Tuple, Union

import enum
import math

from lib.base import Rng

class Facing(enum.Enum):
  NORTH =    0
  EAST  =   90
  SOUTH = -180
  WEST  =  -90

FACING_TYPE = Union[float, Facing, Tuple[float, float]]

def _coerce_facing(pos: Tuple[float, float], facing: FACING_TYPE):
  if isinstance(facing, Facing):
    return facing.value
  elif isinstance(facing, float):
    return facing
  else:
    return 180 * math.atan2(facing[1] - pos[1], facing[0] - pos[0]) / math.pi + 90

class Position(object):
  ENTITY_SCALE = 300

  def __init__(self, translation, rotation, scale=(1, 1, 1)):
    self.tx, self.ty, self.tz = translation
    self.rp, self.ry, self.rr = rotation
    self.sx, self.sy, self.sz = scale

  @classmethod
  def at_center_of_tile(cls, pos: Tuple[int, int], facing: FACING_TYPE = 0):
    x, y = pos
    x += 0.5
    y += 0.5
    return cls((x, y, 0), (0, _coerce_facing((x, y), facing), 0))

  @classmethod
  def randomly_in_tile(
      cls,
      rng: Rng,
      pos: Tuple[int, int],
      facing: Optional[FACING_TYPE] = None):
    x, y = pos
    px = rng.uniform(x, x + 1)
    py = rng.uniform(y, y + 1)
    f = (rng.uniform(-180, 180) if facing is None
         else _coerce_facing(pos, facing))
    return cls((px, py, 0), (0, f, 0))

  def serialize(self, offset: Tuple[int, int]):
    tx = (self.tx + offset[0]) * Position.ENTITY_SCALE
    ty = (self.ty + offset[1]) * Position.ENTITY_SCALE
    tz = self.tz
    return (
      f'Translation: X={tx:.3f} Y={ty:.3f} Z={tz:.3f} '
      f'Rotation: P={self.rp:.6f} Y={self.ry:.6f} R={self.rr:.6f} '
      f'Scale X={self.sx:.3f} Y={self.sy:.3f} Z={self.sz:.3f}'
    )