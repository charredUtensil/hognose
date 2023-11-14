from typing import List

import math

from .space import Space
from lib.base import Context

class Bubble(Space):

  def __init__(self, id: int, x: float, y: float, width: float, height: float):
    self._id = id
    self._x = x
    self._y = y
    self._width = width
    self._height = height
    self._moving = False

  def __repr__(self):
    return (
      f'Bubble {self.id:3d}: '
      f'[{self.left:6.2f},{self.top:6.2f}] '
      f'{self.width:5.2f}x{self.height:5.2f}'
    )

  @property
  def id(self):
    return self._id

  @property
  def left(self):
    return self._x - self._width / 2

  @property
  def top(self):
    return self._y - self._height / 2

  @property
  def right(self):
    return self._x + self._width / 2

  @property
  def bottom(self):
    return self._y + self._height / 2
  
  @property
  def width(self):
    return self._width

  @property
  def height(self):
    return self._height

  @property
  def center(self):
    return self._x, self._y

  @property
  def moving(self):
    return self._moving

  def nudge(self, dx: float, dy: float):
    self._x += dx
    self._y += dy
    self._moving = True

  def overlap(self, other: 'Bubble'):
    x_overlap = _overlap(self._x, other._x, self._width, other._width)
    y_overlap = _overlap(self._y, other._y, self._height, other._height)
    if x_overlap is None or y_overlap is None:
      return (0, 0)
    else:
      return (x_overlap, y_overlap)

  @classmethod
  def from_rng(cls, id: int, context: Context) -> 'Bubble':
    rng    = context.rng['bubble', id]
    x, y   = rng.uniform_point_in_circle(context.bubble_spawn_radius)
    area   = rng.beta(a = 0.2, b = 1.4, min = 4, max = context.bubble_max_area)
    aspect = rng.beta(a = 5, b = 5, min = -0.3, max = 0.3)
    width  = math.sqrt(area) * (abs(aspect) + 1)
    height = area / width
    if aspect < 0:
      width, height = height, width
    return cls(id, x, y, width, height)

  @staticmethod
  def nudge_overlapping(bubbles: List['Bubble']) -> bool:
    moving = False
    for bubble, (vx, vy) in zip(bubbles, _nudge_velocities(bubbles)):
      if abs(vx) + abs(vy) > 0.01:
        moving = True
        bubble.nudge(vx, vy)
      else:
        bubble._moving = False
    return moving

def _overlap(x1, x2, w1, w2):
  """
  Computes the overlap in the given direction.
  \s/x/y/ s/w/h/ for height.
  Returns None if there is no collision, which is different from 0.
  """
  # Compute left and right of both bubbles
  l1 = x1 - w1 / 2
  l2 = x2 - w2 / 2
  r1 = x1 + w1 / 2
  r2 = x2 + w2 / 2
  f = 0
  if x1 > x2 and l1 < r2:
    # Push me to the right
    return r2 - l1
  if x2 > x1 and l2 < r1:
    # Push me to the left
    return l2 - r1
  return None

def _nudge_velocities(bubbles):
  for i, bubble in enumerate(bubbles):
    tfx = 0
    tfy = 0
    for j, other in enumerate(bubbles):
      if i == j:
        continue
      dx, dy = bubble.overlap(other)
      if abs(dx) < abs(dy):
        tfx += dx
      else:
        tfy += dy
    if tfx != 0 or tfy != 0:
      tf = max(1, math.sqrt(tfx * tfx + tfy * tfy))
      yield (tfx / tf, tfy / tf)
    else:
      yield (0, 0)