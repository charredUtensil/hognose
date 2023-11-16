from typing import Optional, Tuple

from lib.base import Rng

class Position(object):
  ENTITY_SCALE = 300

  FACING_NORTH =    0
  FACING_EAST  =   90
  FACING_SOUTH = -180
  FACING_WEST  =  -90

  def __init__(self, translation, rotation, scale=(1, 1, 1)):
    self.tx, self.ty, self.tz = translation
    self.rp, self.ry, self.rr = rotation
    self.sx, self.sy, self.sz = scale

  @classmethod
  def at_center_of_tile(cls, pos: Tuple[int, int], facing: float = 0):
    x, y = pos
    return cls((x + 0.5, y + 0.5, 0), (0, facing, 0))

  @classmethod
  def randomly_in_tile(cls, rng: Rng, pos: Tuple[int, int], facing: Optional[float] = None):
    f = rng.uniform(-180, 180) if facing is None else facing
    x, y = pos
    px = rng.uniform(x, x + 1)
    py = rng.uniform(y, y + 1)
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