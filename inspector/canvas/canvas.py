from typing import Iterable

from inspector.canvas.drawables import Drawable
from inspector.canvas.draw_context import DrawContext

class Canvas():

  def __init__(self):
    self._drawables = {}

  def clear(self):
    self._drawables.clear()

  def push(self, d: Drawable, z: int = 0):
    if z not in self._drawables:
      self._drawables[z] = []
    self._drawables[z].append(d)

  def freeze(self):
    def h():
      for z, dr in sorted(self._drawables.items()):
        yield from dr
    return FrozenCanvas(h())

class FrozenCanvas(Drawable):

  def __init__(self, drawables: Iterable[Drawable]):
    self._drawables = tuple(drawables)

  def draw(self, dc: DrawContext):
    for d in self._drawables:
      d.draw(dc)