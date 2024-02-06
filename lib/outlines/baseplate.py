from typing import Literal

import functools

from lib.outlines.bubble import Bubble
from lib.outlines.space import Space


class Baseplate(Space):
  """A rectangular space that we can build on."""

  AMBIGUOUS = 'ambiguous'
  EXCLUDED = 'excluded'
  SPECIAL = 'special'
  HALL = 'hall'

  def __init__(self, bubble: Bubble, context):
    super().__init__(bubble.id, context)
    self._left = round(bubble.left)
    self._top = round(bubble.top)
    self._right = round(bubble.right)
    self._bottom = round(bubble.bottom)
    self.kind: Literal[
      Baseplate.AMBIGUOUS,
      Baseplate.EXCLUDED,
      Baseplate.SPECIAL,
      Baseplate.HALL
    ] = Baseplate.AMBIGUOUS

  def __repr__(self):
    return (
      f'Baseplate {self.kind} {self.id:3d}: '
      f'[{self.left:4d},{self.top:4d}] '
      f'{self.width:2d}x{self.height:2d}'
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

  @functools.cached_property
  def width(self) -> int:
    return self._right - self._left

  @functools.cached_property
  def height(self) -> int:
    return self._bottom - self._top

  @functools.cached_property
  def center(self):
    return (self.left + self.width / 2, self.top + self.height / 2)

  def is_mergeable(self, other: 'Baseplate'):
    """Returns whether these Baseplates can be combined into one big Cave."""
    for a, b in ((self, other), (other, self)):
      for ua, ub, va1, va2, vb1, vb2 in (
          (a.right, b.left, a.top, a.bottom, b.top, b.bottom),
              (a.bottom, b.top, a.left, a.right, b.left, b.right)):
        if (ua == ub
            and (min(va2, vb2) - max(va1, vb1)
                 > max(va2 - va1, vb2 - vb1) / 2)):
          return True
    return False

  @functools.cached_property
  def pearl_radius(self):
    return min(self.width, self.height) // 2
