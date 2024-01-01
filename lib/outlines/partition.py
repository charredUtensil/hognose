from typing import Iterable, Union

import itertools

from .baseplate import Baseplate
from .bubble import Bubble

class Partition(object):

  def __init__(self, context):
    self.context = context
    self._ids = itertools.count()

    size = context.size // 2
    self.bubbles: List[Bubble] = [Bubble(
        next(self._ids), self.context, -size, -size, size, size)]
    self.baseplates: List[Baseplate] = []

  def step(self):
    for space in self._split(self.bubbles.pop(0)):
      if isinstance(space, Bubble):
        if space.width > 2 and space.height > 2:
          self.bubbles.append(space)
      else:
        self.baseplates.append(space)

  def _cut_vertical(self, bubble: Bubble, x: int) -> Iterable['Bubble']:
    if bubble.left < x and x < bubble.right:
      yield Bubble(
          next(self._ids),
          self.context,
          x, bubble.top, bubble.right, bubble.bottom)
      bubble.right = x
    yield bubble

  def _cut_horizontal(self, bubble: Bubble, y: int) -> Iterable['Bubble']:
    if bubble.top < y and y < bubble.bottom:
      yield Bubble(
          next(self._ids),
          self.context,
          bubble.left, y, bubble.right, bubble.bottom)
      bubble.bottom = y
    yield bubble

  def _split(self, bubble) -> Iterable[Union[Bubble, Baseplate]]:
    rng = bubble.rng['bubble']

    margin = (abs(bubble.width - bubble.height)
        - self.context.baseplate_max_oblongness)
    wide = bubble.width > bubble.height
    def h():
      if margin > 0:
        cut = rng.uniform_int(min = 0, max = margin + 1)
        if wide:
          cut1 = bubble.left + cut
          cut2 = bubble.right + cut - margin
          for b in self._cut_vertical(bubble, cut1):
            yield from self._cut_vertical(b, cut2)
        else:
          cut1 = bubble.top + cut
          cut2 = bubble.bottom + cut - margin
          for b in self._cut_horizontal(bubble, cut1):
            yield from self._cut_horizontal(b, cut2)
      else:
        if (bubble.area() <= self.context.baseplate_max_area
            and rng.chance(0.85)):
          yield Baseplate(bubble, self.context)
        elif wide:
          x = rng.beta_int(min=bubble.left + 1, max=bubble.right)
          yield from self._cut_vertical(bubble, x)
        else:
          y = rng.beta_int(min=bubble.top + 1, max=bubble.bottom)
          yield from self._cut_horizontal(bubble, y)
    r = tuple(h())
    if len(r) > 2:
      if wide:
        r[0].top += 1
        r[-1].bottom -= 1
      else:
        r[0].left += 1
        r[-1].right -= 1
    return r
    