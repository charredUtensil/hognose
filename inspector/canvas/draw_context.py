from typing import Tuple, Union

from inspector.canvas.vectors import BaseVector, XVector, YVector


class DrawContext():
  def __init__(self, surface, scale, offset_x, offset_y):
    self.surface = surface
    self.scale = scale
    self.width = surface.get_width()
    self.height = surface.get_height()
    self.center_x = self.width / 2
    self.center_y = self.height / 2
    self.origin_x = self.center_x + scale * offset_x
    self.origin_y = self.center_y + scale * offset_y
    self._anchors = {
        XVector.Anchor.CENTER_X: self.center_x,
        XVector.Anchor.ORIGIN_X: self.origin_x,
        XVector.Anchor.LEFT: 0,
        XVector.Anchor.RIGHT: self.width,
        YVector.Anchor.CENTER_Y: self.center_y,
        YVector.Anchor.ORIGIN_Y: self.origin_y,
        YVector.Anchor.TOP: 0,
        YVector.Anchor.BOTTOM: self.height}

  def tr(self, v: Union[BaseVector, Tuple[BaseVector, ...]]):
    if isinstance(v, BaseVector):
      return v.tr(self)
    return tuple(vv.tr(self) for vv in v)
