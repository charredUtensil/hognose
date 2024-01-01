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

    self.baseplate_max_size = round(
        context.size * context.baseplate_max_side_ratio)

  def step(self):
    queue = list(self.bubbles)
    self.bubbles.clear()
    for bubble in queue:
      for space in self._split(bubble):
        if isinstance(space, Bubble):
          if space.width > 2 and space.height > 2:
            self.bubbles.append(space)
        else:
          self.baseplates.append(space)

  def _clone(self, bubble: Bubble, left=None, top=None, right=None, bottom=None) -> Bubble:
    return Bubble(
        next(self._ids),
        self.context,
        bubble.left if left is None else left,
        bubble.top if top is None else top,
        bubble.right if right is None else right,
        bubble.bottom if bottom is None else bottom)

  def _split(self, bubble) -> Iterable[Union[Bubble, Baseplate]]:
    rng = bubble.rng['bubble']

    if bubble.width > bubble.height * 2:
      # Cut vertically
      x = rng.beta_int(min=bubble.left + 1, max=bubble.right)
      yield self._clone(bubble, left = x)
      bubble.right = x
      yield bubble
    elif bubble.height > bubble.width * 2:
      # Cut horizontally
      y = rng.beta_int(min=bubble.top + 1, max=bubble.bottom)
      yield self._clone(bubble, top = y)
      bubble.bottom = y
      yield bubble
    else:
      # Cut out from center
      w = rng.beta_int(a = 5, b = 2.5, min = 3, max = bubble.width)
      h = rng.beta_int(a = 5, b = 2.5, min = 3, max = bubble.height)
      w = min(w, h + self.context.baseplate_max_oblongness)
      h = min(h, w + self.context.baseplate_max_oblongness)
      x1 = rng.uniform_int(min = bubble.left, max = bubble.right - w)
      y1 = rng.uniform_int(min = bubble.top,  max = bubble.bottom - h)
      x2 = x1 + w
      y2 = y1 + h
      if rng.chance(0.5):
        yield self._clone(bubble, right = x1, bottom = y2)
        yield self._clone(bubble, left  = x1, bottom = y1)
        yield self._clone(bubble, left  = x2, top    = y1)
        yield self._clone(bubble, right = x2, top    = y2)
      else:
        yield self._clone(bubble, right = x2, bottom = y1)
        yield self._clone(bubble, left  = x2, bottom = y2)
        yield self._clone(bubble, left  = x1, top    = y2)
        yield self._clone(bubble, right = x1, top    = y1)
      bubble.left   = x1
      bubble.top    = y1
      bubble.right  = x2
      bubble.bottom = y2
      if max(w, h) <= self.baseplate_max_size:
        yield Baseplate(bubble, self.context)
      else:
        yield bubble
    