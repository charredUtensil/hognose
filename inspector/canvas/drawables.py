from typing import Optional, Tuple

import abc
import enum
import functools
import pygame
import math

from inspector.canvas.draw_context import DrawContext
import inspector.canvas.vectors as v

class Drawable(abc.ABC):

  @abc.abstractmethod
  def draw(self, dc: DrawContext):
    pass

Color = Tuple[int, int, int]

class Fill(Drawable):

  def __init__(self, color):
    self._color: Color = color

  def draw(self, dc):
    dc.surface.fill(self._color)

class Line(Drawable):

  def __init__(self, color, start, end, thickness = v.a(1)):
    self._color: Color = color
    self._start = v.xy(start)
    self._end = v.xy(end)
    self._thickness = v.a(thickness)

  def draw(self, dc):
    thickness = max(1, math.floor(dc.tr(self._thickness)))
    pygame.draw.line(
        dc.surface,
        self._color,
        dc.tr(self._start),
        dc.tr(self._end),
        thickness)

class Circle(Drawable):

  def __init__(self, color, origin, radius, thickness = v.a(0)):
    self._color: Color = color
    self._origin = v.xy(origin)
    self._radius = v.s(radius)
    self._thickness = v.a(thickness)

  def draw(self, dc):
    pygame.draw.circle(
      dc.surface,
      self._color,
      dc.tr(self._origin),
      max(dc.tr(self._radius), 1),
      dc.tr(self._thickness))

class Rect(Drawable):
  def __init__(self, color, rect, thickness = v.a(0)):
    self._color: Color = color
    self._rect = v.xywh(rect)
    self._thickness = v.a(thickness)

  def draw(self, dc):
    pygame.draw.rect(
      dc.surface,
      self._color,
      pygame.Rect(*dc.tr(self._rect)),
      dc.tr(self._thickness))

class Font():
  def __init__(self, *args, **kwargs):
    self._args = args
    self._kwargs = kwargs

  @functools.cached_property
  def proxied(self):
    return pygame.font.SysFont(*self._args, **self._kwargs)

class Gravity(enum.Enum):
  TOP_LEFT = (-1, -1)
  LEFT = (-1, 0)
  BOTTOM_LEFT = (-1, 1)
  TOP = (0, -1)
  CENTER = (0, 0)
  BOTTOM = (0, 1)
  TOP_RIGHT = (1, -1)
  RIGHT = (1, 0)
  BOTTOM_RIGHT = (1, 1)

  def __iter__(self):
    return iter(self.value)

class RawText():

  def __init__(self, font, text, gravity):
    self._font: Font = font
    self._text: str = text
    self._gravity: Gravity = gravity

  @functools.cached_property
  def _measurements(self):
    gx, gy = self._gravity
    _, th = self._font.proxied.size('M')
    lines = self._text.splitlines()
    def h():
      for i, line in enumerate(lines):
        tw, _ = self._font.proxied.size(line)
        ox = 0
        oy = th * i
        if gx >= 0:
          ox -= tw * (0.5 if gx == 0 else 1)
        if gy >= 0:
          oy -= th * len(lines) * (0.5 if gy == 0 else 1)
        yield i, line, ox, oy
    return tuple(h())

  def draw(self, dc, color, origin):
    x0, y0 = dc.tr(origin)
    for i, line, ox, oy in self._measurements:
      font_surface = self._font.proxied.render(line, False, color)
      dc.surface.blit(font_surface, (x0 + ox, y0 + oy))

class Label(Drawable):

  def __init__(
      self,
      font,
      text,
      color,
      origin,
      shadow_color = None,
      shadow_offset = v.a(0),
      gravity = Gravity.CENTER):
    self._rt = RawText(font, text, gravity)
    self._color: Color = color
    self._origin = v.xy(origin)
    self._shadow_color: Optional[Color] = shadow_color
    self._shadow_offset = v.a(shadow_offset)

  def draw(self, dc):
    if self._shadow_color:
      x, y = self._origin
      self._rt.draw(dc, self._shadow_color, (x + self._shadow_offset, y + self._shadow_offset))
    self._rt.draw(dc, self._color, self._origin)

class LabelIfFits(Drawable):
  def __init__(
      self,
      font,
      text,
      color,
      rect,
      shadow_color = None,
      shadow_offset = v.a(0),
      gravity=Gravity.CENTER,
      fallback=None):
    self._rt = RawText(font, text, gravity)
    self._font: Font = font
    self._text: str = text
    self._color: Color = color
    self._rect = v.xywh(rect)
    self._shadow_color: Optional[Color] = shadow_color
    self._shadow_offset = v.a(shadow_offset)
    self._gravity: Gravity = gravity
    self._fallback: Optional[Drawable] = fallback

  @functools.cached_property
  def min_size(self):
    dims = tuple(
        self._font.proxied.size(line) for line in self._text.splitlines())
    return max(w for w, h in dims), sum(h for w, h in dims)

  @functools.cached_property
  def _text_origin(self):
    x, y, w, h = self._rect
    gx, gy = self._gravity
    if gx == 0:
      x += w / 2
    elif gx > 0:
      x += w
    if gy == 0:
      y += h / 2
    elif gy > 0:
      y += h
    return x, y

  def draw(self, dc):
    x, y, w, h = dc.tr(self._rect)
    min_w, min_h = self.min_size
    if (w > min_w) and (h > min_h):
      tx, ty = self._text_origin
      if self._shadow_color:
        self._rt.draw(
            dc,
            self._shadow_color,
            (tx + self._shadow_offset, ty + self._shadow_offset))
      self._rt.draw(dc, self._color, (tx, ty))
    elif self._fallback:
      self._fallback.draw(dc)

class RadialLabel(Drawable):
  def __init__(self, font, text, fg_color, bg_color, origin, inset=v.a(50)):
    self._rt: RawText = RawText(font, text, Gravity.CENTER)
    self._fg_color: Color = fg_color
    self._bg_color: Color = bg_color
    self._origin = v.xy(origin)
    self._inset = v.a(inset)

  def draw(self, dc):
    points_x, points_y = dc.tr(self._origin)
    theta = math.atan2(points_y - dc.center_y, points_x - dc.center_x)
    sin = math.sin(theta)
    cos = math.cos(theta)
    radius = min((
        abs(r) for r
        in (dc.tr(v.CENTER_Y - self._inset) / sin if sin != 0 else None,
            dc.tr(v.CENTER_X - self._inset) / cos if cos != 0 else None)
        if r is not None))
    label_x = radius * cos + dc.center_x
    label_y = radius * sin + dc.center_y

    # Line from point to label
    pygame.draw.line(
        dc.surface,
        self._fg_color,
        (label_x, label_y),
        (points_x, points_y))

    # Background circle
    pygame.draw.circle(
      dc.surface,
      self._bg_color,
      (label_x, label_y),
      10)

    # Border circle
    pygame.draw.circle(
      dc.surface,
      self._fg_color,
      (label_x, label_y),
      10,
      1)
    
    # Label
    self._rt.draw(dc, self._fg_color, (v.a(label_x), v.a(label_y)))


