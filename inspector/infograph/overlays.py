from inspector.canvas import Canvas, Gravity, Label, v
from inspector.infograph.common import (
    FONT_BIG, FONT_MED, Z_OVERLAY, OVERLAY_COLOR, OVERLAY_PADDING,
    OVERLAY_SHADOW_COLOR, OVERLAY_SHADOW_OFFSET, WARNING_COLOR)


def _title(cavern):
  name = cavern.diorama.level_name or f'0x{cavern.context.seed:08x}'
  return f'{name} {cavern.stage}'


def _description(cavern):
  if cavern.stage == 'init':
    return str(cavern.context)
  if cavern.stage == 'script':
    return ''
  if cavern.stage == 'fence':
    t = cavern.context.size
    _, _, w, h = cavern.diorama.bounds
    return f'Target size: {t}x{t}\nActual size: {w}x{h}'
  if cavern.stage == 'serialize':
    return (
        f'{len(cavern.diorama.script):d} script lines\n'
        f'Total file size: {len(cavern.serialized)//1024:d}kB')
  if cavern.diorama.briefing:
    return _word_wrap(cavern.diorama.briefing, 60)
  if cavern.diorama.objectives:
    return '\n'.join(
        o.description for o in cavern.diorama.objectives)
  if cavern.conquest:
    cy = cavern.diorama.crystal_yield
    ce = sum(p.expected_crystals for p in cavern.conquest.somatic_planners)
    crystals = f'{cy:d}/{ce:d}' if cy and ce and cy != ce else f'{ce:d}'
    ore = cavern.diorama.ore_yield
    return f'{crystals} EC\n{ore:d} Ore'
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


def push_overlays(canvas: Canvas, cavern, details, warnings):
  pc = Canvas()
  detail_str = f'{details}\n' if details else ''
  pc.push(Label(
      font=FONT_MED,
      text=detail_str + _description(cavern),
      color=OVERLAY_COLOR,
      origin=(v.LEFT + OVERLAY_PADDING, v.BOTTOM - OVERLAY_PADDING),
      shadow_color=OVERLAY_SHADOW_COLOR,
      shadow_offset=OVERLAY_SHADOW_OFFSET,
      gravity=Gravity.BOTTOM_LEFT))
  pc.push(Label(
      font=FONT_BIG,
      text=_title(cavern),
      color=OVERLAY_COLOR,
      origin=(v.LEFT + OVERLAY_PADDING, v.TOP + OVERLAY_PADDING),
      shadow_color=OVERLAY_SHADOW_COLOR,
      shadow_offset=OVERLAY_SHADOW_OFFSET,
      gravity=Gravity.TOP_LEFT))
  pc.push(Label(
      font=FONT_MED,
      text='\n'.join(warnings),
      color=WARNING_COLOR,
      origin=(v.RIGHT - OVERLAY_PADDING, v.BOTTOM - OVERLAY_PADDING),
      shadow_color=OVERLAY_SHADOW_COLOR,
      shadow_offset=OVERLAY_SHADOW_OFFSET,
      gravity=Gravity.BOTTOM_RIGHT))
  canvas.push(pc.freeze(), Z_OVERLAY)
