from typing import Union

import itertools

from inspector.canvas import Canvas, Gravity, Rect, LabelIfFits, Line, v
from inspector.infograph.common import FONT_TINY, Z_SPACES, Z_PATHS
from lib.outlines import Bubble, Baseplate, Path


BUBBLE_OUTLINE_COLOR = (0x10, 0x00, 0x77)
BUBBLE_LABEL_COLOR = (0x77, 0x77, 0xff)

BASEPLATE_COLORS = {
    Baseplate.AMBIGUOUS: (
        (0x20, 0x20, 0x20), (0x40, 0x40, 0x40), (0x77, 0x77, 0x77)),
    Baseplate.EXCLUDED: (None, None, None),
    Baseplate.SPECIAL: ((0x77, 0x00, 0x10), None, (0xff, 0x77, 0x77)),
    Baseplate.HALL: ((0x44, 0x00, 0x08), None, None),
}

PATH_COLORS = {
    Path.AMBIGUOUS: (0x66, 0x66, 0x66),
    Path.EXCLUDED: None,
    Path.SPANNING: (0xff, 0xff, 0x00),
    Path.AUXILIARY: (0xcc, 0xcc, 0xcc),
}

def _space_rect(space: Union[Bubble, Baseplate]):
  return (
      space.left,
      space.top,
      space.width,
      space.height)


def push_outlines(canvas: Canvas, bubbles, baseplates, paths):
  pc = Canvas()
  for b in bubbles:
    rect = _space_rect(b)
    pc.push(Rect(
        color = BUBBLE_OUTLINE_COLOR,
        rect = rect,
        thickness = v.a(1)))
    pc.push(LabelIfFits(
        font=FONT_TINY,
        text=f'{b.id:03d}',
        color=BUBBLE_LABEL_COLOR,
        rect=rect,
        gravity=Gravity.TOP_LEFT))
  for bp in baseplates:
    color, ocolor, lcolor = BASEPLATE_COLORS[bp.kind]
    rect = _space_rect(bp)
    if color:
      pc.push(Rect(
          color = color,
          rect = rect))
    if ocolor:
      pc.push(Rect(
          color = color,
          rect = rect))
    if lcolor:
      pc.push(LabelIfFits(
          font=FONT_TINY,
          text=f'{bp.id:03d}',
          color=lcolor,
          rect=rect,
          gravity=Gravity.TOP_LEFT), 1)
  canvas.push(pc.freeze(), Z_SPACES)
  pc.clear()
  for path in paths:
    color = PATH_COLORS[path.kind]
    if not color:
      continue
    for a, b in itertools.pairwise(path.baseplates):
      pc.push(Line(
          color=color,
          start=a.center,
          end=b.center,
          thickness=v.a(3) if path.kind == Path.SPANNING else v.a(2)))
  canvas.push(pc.freeze(), Z_PATHS)