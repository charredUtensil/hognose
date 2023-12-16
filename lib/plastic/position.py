from typing import Optional, Tuple, Union

import enum
import math

from lib.base import Rng

class Facing(enum.Enum):
  NORTH = math.pi / -2
  EAST  = 0
  SOUTH = math.pi / 2
  WEST  = math.pi

FACING_TYPE = Union[float, Facing, Tuple[float, float]]

def _coerce_facing(pos: Tuple[float, float], facing: FACING_TYPE):
  if isinstance(facing, Facing):
    return facing.value
  elif isinstance(facing, float):
    return facing
  else:
    return math.atan2(facing[1] - pos[1], facing[0] - pos[0])

class Position(object):
  ENTITY_SCALE = 300

  def __init__(self, translation, rotation, scale=(1, 1, 1)):
    self.tx, self.ty, self.tz = translation
    self.rp, self.ry, self.rr = rotation
    self.sx, self.sy, self.sz = scale

  def __copy__(self):
    return Position(
        (self.tx, self.ty, self.tz),
        (self.rp, self.ry, self.rr),
        (self.sx, self.sy, self.sz))

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
    f = (rng.uniform(-math.pi, math.pi) if facing is None
         else _coerce_facing(pos, facing))
    return cls((px, py, 0), (0, f, 0))

  def serialize(
      self,
      offset: Tuple[int, int],
      rotation_offset: float = 0):
    tx = (self.tx + offset[0]) * Position.ENTITY_SCALE
    ty = (self.ty + offset[1]) * Position.ENTITY_SCALE
    tz = self.tz
    rp = rads_to_degrees(self.rp)
    ry = rads_to_degrees(self.ry) + rotation_offset
    rr = rads_to_degrees(self.rr)
    return (
      f'Translation: X={tx:.3f} Y={ty:.3f} Z={tz:.3f} '
      f'Rotation: P={rp:.6f} Y={ry:.6f} R={rr:.6f} '
      f'Scale X={self.sx:.3f} Y={self.sy:.3f} Z={self.sz:.3f}'
    )

def rads_to_degrees(rads: float):
  return (rads * 180 / math.pi + 180) % 360 - 180