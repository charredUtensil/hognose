from typing import Iterable, Optional, Tuple, Union

Color = Tuple[int, int, int]

import math
import pygame

class AbsoluteScreenCoord(object):
  def __init__(self, value: int):
    self.value = value

class RelativeScreenCoord(object):
  def __init__(self, percent: float):
    self.percent = percent

Coord = Union[float, AbsoluteScreenCoord, RelativeScreenCoord]

class DrawContext(object):
  def __init__(self, surface, scale):
    self.surface = surface
    self.scale = scale
    self.width = surface.get_width()
    self.height = surface.get_height()
    self.ox = self.width / 2
    self.oy = self.height / 2
  
  def sx(self, x: Coord):
    if isinstance(x, AbsoluteScreenCoord):
      return x.value
    if isinstance(x, RelativeScreenCoord):
      return x.percent * self.width
    return self.scale * x + self.ox

  def sy(self, y: Coord):
    if isinstance(y, AbsoluteScreenCoord):
      return y.value
    if isinstance(y, RelativeScreenCoord):
      return y.percent * self.height
    return self.scale * y + self.oy

class Frame(object):

  def __init__(self):
    self._calls = []

  def playback(self, surface, scale):
    dc = DrawContext(surface, scale)
    for call in self._calls:
      call(dc)

  def draw_line(
      self,
      color: Color,
      start: Tuple[Coord, Coord],
      end: Tuple[Coord, Coord],
      width: int = 1):

    def draw(dc):
      pygame.draw.line(
          dc.surface,
          color,
          (dc.sx(start[0]), dc.sy(start[1])),
          (dc.sx(end[0]),   dc.sy(end[1])),
          width)
    self._calls.append(draw)

  def draw_circle(
      self,
      color: Color,
      origin: Tuple[Coord, Coord],
      radius: float,
      width: int = 0):
    def draw(dc):
      pygame.draw.circle(
        dc.surface,
        color,
        (dc.sx(origin[0]), dc.sy(origin[1])),
        radius,
        width)
    self._calls.append(draw)

  def draw_rect(
      self,
      color: Color,
      rect: pygame.Rect,
      lineWidth: int = 0):
    left, top, width, height = rect
    def draw(dc):
      pygame.draw.rect(
        dc.surface,
        color,
        pygame.Rect(
          dc.sx(left),
          dc.sy(top),
          dc.scale * width,
          dc.scale * height),
        lineWidth)
    self._calls.append(draw)

  def draw_label_for_points(
      self,
      font,
      text: str,
      fg_color: Color,
      bg_color: Color,
      points: Iterable[Tuple[Coord, Coord]]):

    def draw(dc):
      pass
    self._calls.append(draw)

  def draw_label_for_rect(
      self,
      font,
      text: str,
      fg_color: Color,
      bg_color: Color,
      rect: pygame.Rect,
      gravity: Tuple[int, int]):

    dims = tuple(font.size(line) for line in text.splitlines())
    text_sw = max(w for w, h in dims)
    text_sh = sum(h for w, h in dims)
    del dims
    inplace_infos = tuple(_text_infos(font, text, (-n for n in gravity)))
    radial_infos  = tuple(_text_infos(font, text, (0, 0)))

    left, top, width, height = rect

    gx, gy = gravity
    ox = 0
    if gx == 0:
      ox = width / 2
    elif gx > 0:
      ox = width
    oy = 0
    if gy == 0:
      oy = height / 2
    elif gy > 0:
      oy = height

    def draw(dc):
      if (width * dc.scale > text_sw) and (height * dc.scale > text_sh):
        # Text fits in rect; draw it inplace in rect
        _draw_text_lines(
          dc,
          font,
          fg_color,
          (AbsoluteScreenCoord(dc.sx(left + ox)), AbsoluteScreenCoord(dc.sy(top + oy))),
          inplace_infos)
      else:
        # draw a radial label pointing to the position
        _draw_radial_label(
          dc,
          font,
          fg_color,
          bg_color,
          (left + width / 2, top + height / 2),
          radial_infos)
    self._calls.append(draw)

  def draw_text(
      self,
      font,
      text: str,
      color: Color,
      position: Tuple[Coord, Coord],
      gravity: Tuple[int, int]):
    infos = tuple(_text_infos(font, text, gravity))
    def draw(dc):
      _draw_text_lines(
          dc,
          font,
          color,
          position,
          infos)
    self._calls.append(draw)

TextInfos = Iterable[Tuple[int, str, float, float]]

def _text_infos(
    font,
    text: str,
    gravity: Tuple[int, int]) -> TextInfos:
  gx, gy = gravity
  _, th = font.size('M')
  lines = text.splitlines()
  for i, line in enumerate(lines):
    tw, _ = font.size(line)
    ox = 0
    oy = th * i
    if gx <= 0:
      ox -= tw * (0.5 if gx == 0 else 1)
    if gy <= 0:
      oy -= th * len(lines) * (0.5 if gy == 0 else 1)
    yield i, line, ox, oy

def _draw_text_lines(
    dc,
    font,
    color: Color,
    position: Tuple[Coord, Coord],
    infos: TextInfos):
  for i, line, ox, oy in infos:
    font_surface = font.render(line, False, color)
    x = dc.sx(position[0]) + ox
    y = dc.sy(position[1]) + oy
    dc.surface.blit(font_surface, (x, y))

def _draw_radial_label(
    dc,
    font,
    fg_color: Color,
    bg_color: Optional[Color],
    origin: Tuple[Coord, Coord],
    infos: TextInfos):
  cx, cy = origin
  theta = math.atan2(cy, cx)
  sin = math.sin(theta)
  cos = math.cos(theta)
  radius = min((
      abs(r) for r
      in ((dc.oy - 50) / sin if sin != 0 else None,
          (dc.ox - 50) / cos if cos != 0 else None)
      if r is not None))

  label_sx = radius * cos + dc.ox
  label_sy = radius * sin + dc.oy
  pygame.draw.line(
      dc.surface,
      fg_color,
      (label_sx, label_sy),
      (dc.sx(cx), dc.sy(cy)))
  pygame.draw.circle(
    dc.surface,
    bg_color or (0, 0, 0),
    (label_sx, label_sy),
    10)
  pygame.draw.circle(
    dc.surface,
    fg_color,
    (label_sx, label_sy),
    10,
    1)
  _draw_text_lines(
      dc,
      font,
      fg_color,
      (AbsoluteScreenCoord(label_sx), AbsoluteScreenCoord(label_sy)),
      infos)