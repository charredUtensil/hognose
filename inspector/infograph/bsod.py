from inspector.canvas import Canvas, Fill, Gravity, Label, v
from inspector.infograph.common import FONT_MED, FONT_BIG

import traceback

BSOD_FG_COLOR = (0xff, 0xff, 0xff)
BSOD_BG_COLOR = (0x22, 0x22, 0xDD)

def push_bsod(canvas: Canvas, seed: int, exception: Exception):
    canvas.push(Fill(BSOD_BG_COLOR))
    canvas.push(Label(
      font=FONT_BIG,
      text=f'{type(exception).__name__} in 0x{seed >> 16:X}_{seed & 0xFFFF}',
      color=BSOD_FG_COLOR,
      origin=(v.LEFT + v.a(25), v.TOP + v.a(25)),
      gravity=Gravity.TOP_LEFT))
    canvas.push(Label(
      font=FONT_MED,
      text=''.join(traceback.format_exception(
          type(exception), exception, exception.__traceback__)),
      color=BSOD_FG_COLOR,
      origin=(v.LEFT + v.a(25), v.TOP + v.a(50)),
      gravity=Gravity.TOP_LEFT))