from typing import Literal

import enum
import math

from .bubble import Bubble
from .space import Space

from lib.base import ProceduralThing

class Baseplate(ProceduralThing, Space):
  AMBIGUOUS = 'ambiguous'
  EXCLUDED  = 'excluded'
  SPECIAL   = 'special'
  HALL      = 'hall'

  def __init__(self, bubble: Bubble, context):
    super().__init__(bubble.id, context)
    self._left   = round(bubble.left)
    self._top    = round(bubble.top)
    self._right  = round(bubble.right)
    self._bottom = round(bubble.bottom)
    self._width  = self._right - self._left
    self._height = self._bottom - self._top
    self._x      = self._left + self._width / 2
    self._y      = self._top + self._height / 2
    self.kind: Literal[
      Baseplate.AMBIGUOUS,
      Baseplate.EXCLUDED,
      Baseplate.SPECIAL,
      Baseplate.HALL
      ]          = Baseplate.AMBIGUOUS

  def __repr__(self):
    return (
      f'Baseplate {self.kind} {self.id:3d}: '
      f'[{self._left:4d},{self._top:4d}] '
      f'{self._width:2d}x{self._height:2d}'
    )

  @property
  def left(self) -> int:
    return self._left

  @property
  def top(self) -> int:
    return self._top

  @property
  def right(self) -> int:
    return self._right

  @property
  def bottom(self) -> int:
    return self._bottom
  
  @property
  def width(self) -> int:
    return self._width

  @property
  def height(self) -> int:
    return self._height

  @property
  def center(self):
    return self._x, self._y

  def is_mergeable(self, other: 'Baseplate'):
    for a, b in ((self, other), (other, self)):
      for ua, ub, va1, va2, vb1, vb2 in (
        (a._right, b._left, a._top, a._bottom, b._top, b._bottom),
        (a._bottom, b._top, a._left, a._right, b._left, b._right)):
        if ua == ub and min(va2, vb2) - max(va1, vb1) > max(va2 - va1, vb2 - vb1) / 2:
          return True
    return False

  @property
  def pearl_radius(self):
    return min(self.width, self.height) // 2