from typing import Optional

from inspector.canvas import Drawable, FrozenCanvas, Gravity, Label, Rect, v
from inspector.infograph.common import (
    FONT_BIG, OVERLAY_COLOR, OVERLAY_PADDING, OVERLAY_SHADOW_COLOR,
    OVERLAY_SHADOW_OFFSET)


class UiOverlay(Drawable):

  def __init__(self):
    self._index_label: Optional[Drawable] = None
    self._progress_bg: Optional[Drawable] = None
    self._progress_fg: Optional[Drawable] = None

    self._index: int = 0
    self._progress: float = 0
    self._total: int = 0

  def update(self, /, index, total, progress):
    if index != self._index or total != self._total:
      self._index_label = None
      self._index = index
      self._total = total
    if progress != self._progress:
      self._progress_fg = None
      self._progress = progress

  def draw(self, dc):
    if self._total > 1:
      if not self._index_label:
        self._index_label = Label(
            font=FONT_BIG,
            text=f'{self._index + 1} / {self._total}',
            color=OVERLAY_COLOR,
            origin=(v.RIGHT - OVERLAY_PADDING, v.TOP + OVERLAY_PADDING),
            shadow_color=OVERLAY_SHADOW_COLOR,
            shadow_offset=OVERLAY_SHADOW_OFFSET,
            gravity=Gravity.TOP_RIGHT)
      self._index_label.draw(dc)
    if self._progress < 1:
      if not self._progress_fg:
        w = v.a(400)
        h = v.a(20)
        self._progress_fg = Rect(
            color=OVERLAY_COLOR,
            rect=(
                v.CENTER_X - w // 2,
                v.CENTER_Y - h // 2,
                w * self._progress,
                h))
        if not self._progress_bg:
          self._progress_bg = FrozenCanvas((
              Rect(
                  color=OVERLAY_SHADOW_COLOR,
                  rect=(
                      v.CENTER_X - w // 2 + OVERLAY_SHADOW_OFFSET,
                      v.CENTER_Y - h // 2 + OVERLAY_SHADOW_OFFSET,
                      w, h)),
              Rect(
                  color=OVERLAY_COLOR,
                  rect=(v.CENTER_X - w // 2, v.CENTER_Y - h // 2, w, h),
                  thickness=2)))
      self._progress_bg.draw(dc)
      self._progress_fg.draw(dc)
