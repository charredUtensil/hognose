from inspector.canvas import Canvas, Gravity, Label, v
from inspector.infograph.common import FONT_BIG, FONT_MED, Z_OVERLAY

OVERLAY_COLOR = (0x44, 0xff, 0x88)
OVERLAY_SHADOW_COLOR = (0x00, 0x00, 0x00)
WARNING_COLOR = (0xff, 0xff, 0x00)

PADDING = v.a(10)

def _title(cavern):
  name = cavern.diorama.level_name or f'{cavern.context.seed:x}'
  return f'{name} {cavern.stage}'

def _description(cavern):
  if cavern.diorama.briefing:
    return _word_wrap(cavern.diorama.briefing, 60)
  elif cavern.diorama.objectives:
    return '\n'.join(
        o.description for o in cavern.diorama.objectives)
  elif cavern.conquest:
    crystals = (
      cavern.diorama.crystal_yield or
      sum(p.expected_crystals for p in cavern.conquest.somatic_planners)
    )
    ore = cavern.diorama.ore_yield
    return f'{crystals:d} EC\n{ore:d} Ore'
  return ''

def _word_wrap(text: str, chars: int):
  def h():
    for line in text.splitlines():
      while line:
        if len(line) <= chars:
          yield line
          break
        ptr = chars
        while ptr > 0:
          if line[ptr].isspace():
            yield line[:ptr]
            line = line[ptr + 1:]
            break
          ptr -= 1
        else:
          yield line[:chars]
          line = line[chars:]
  return '\n'.join(h())


def push_overlays(canvas: Canvas, cavern, warnings):
  pc = Canvas()
  pc.push(Label(
      font=FONT_BIG,
      text=_title(cavern),
      color=OVERLAY_COLOR,
      origin=(v.LEFT + PADDING, v.TOP + PADDING),
      shadow_color=OVERLAY_SHADOW_COLOR,
      shadow_offset=v.a(2),
      gravity = Gravity.TOP_LEFT))
  pc.push(Label(
      font=FONT_MED,
      text=_description(cavern),
      color=OVERLAY_COLOR,
      origin=(v.LEFT + PADDING, v.BOTTOM - PADDING),
      shadow_color=OVERLAY_SHADOW_COLOR,
      shadow_offset=v.a(2),
      gravity=Gravity.BOTTOM_LEFT))
  pc.push(Label(
      font=FONT_MED,
      text='\n'.join(warnings),
      color=WARNING_COLOR,
      origin=(v.RIGHT - PADDING, v.BOTTOM - PADDING),
      shadow_color=OVERLAY_SHADOW_COLOR,
      shadow_offset=v.a(2),
      gravity=Gravity.BOTTOM_RIGHT))
  canvas.push(pc.freeze(), Z_OVERLAY)