from typing import List, Tuple

import itertools
import re

from inspector.canvas import Canvas, LabelIfFits, Line, Rect, v
from inspector.infograph.common import FONT_TINY, Z_SCRIPT
from lib.plastic import ScriptFragment

POI_LABEL_COLOR = (0x00, 0x00, 0x00)
POI_PATH_COLOR = (0xff, 0xff, 0xff)
POI_COLOR = (0x00, 0xff, 0xff)

POI_RE = re.compile(r'y@(-?\d+),x@(-?\d+)')

def push_script(canvas: Canvas, details):
  pc = Canvas()
  if isinstance(details, ScriptFragment):
    poi: List[Tuple[int, int]] = []
    for y, x in POI_RE.findall(str(details)):
      poi.append((int(y), int(x)))
    for (y1, x1), (y2, x2) in itertools.pairwise(poi):
      pc.push(Line(
          color=POI_PATH_COLOR,
          start=(x1 + 0.5, y1 + 0.5),
          end=(x2 + 0.5, y2 + 0.5),
          thickness=v.s(0.5)))
    for i, (y, x) in enumerate(poi):
      pc.push(Rect(
          color=POI_COLOR,
          rect=(x, y, 1, 1)))
      pc.push(LabelIfFits(
          color=POI_LABEL_COLOR,
          font=FONT_TINY,
          rect=(x, y, 1, 1),
          text=str(i)))
    canvas.push(pc.freeze(), Z_SCRIPT)