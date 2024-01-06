from typing import Iterable, List

import itertools
import math

from .space import Space
from lib.base import Context

class Bubble(Space):

  def __init__(self, id: int, context, left: int, top: int, right: int, bottom: int):
    super().__init__(id, context)
    self.left = left
    self.top = top
    self.right = right
    self.bottom = bottom

  def __repr__(self):
    return (
      f'Bubble {self.id:3d}: '
      f'[{self.left:4d},{self.top:4d}] '
      f'{self.width:2d}x{self.height:2d}'
    )
  
  @property
  def width(self):
    return self.right - self.left

  @property
  def height(self):
    return self.bottom - self.top

  @property
  def center(self):
    return (self.left + self.right) / 2, (self.top + self.bottom) / 2