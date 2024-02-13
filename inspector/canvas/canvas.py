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
    return FrozenCanvas(self)

class FrozenCanvas(Drawable):

  def __init__(self, canvas: Canvas):
    def h():
      for z, dr in sorted(canvas._drawables.items()):
        yield from dr
    self._drawables = tuple(h())

  def draw(self, dc: DrawContext):
    for d in self._drawables:
      d.draw(dc)