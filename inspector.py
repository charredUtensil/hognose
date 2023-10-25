from typing import Tuple

import itertools
import math
import pygame

from lib.outlines import Bubble, Baseplate, Path
from lib.planners import StemPlanner
from lib.plastic import Tile

TITLE_COLOR            = (0x00, 0xff, 0x22)
BUBBLE_COLOR           = (0x10, 0x00, 0x77)
BUBBLE_LABEL_COLOR     = (0xff, 0xff, 0xff)
BASEPLATE_COLORS = {
  Baseplate.AMBIGUOUS  : (0x40, 0x40, 0x40),
  Baseplate.EXCLUDED   : None,
  Baseplate.SPECIAL    : (0x77, 0x00, 0x10),
  Baseplate.HALL       : (0x44, 0x00, 0x08),
}
BASEPLATE_LABEL_COLOR  = (0x00, 0x00, 0x00)
PATH_COLORS = {
  Path.AMBIGUOUS       : (0x66, 0x66, 0x66),
  Path.EXCLUDED        : None,
  Path.SPANNING        : (0xff, 0xff, 0x00),
  Path.AUXILIARY       : (0x44, 0xff, 0x00),
}
CRYSTAL_COLOR          = Tile.CRYSTAL_SEAM.inspect_color
BUILDING_COLOR         = (0xFF, 0xFF, 0x00)

BUILDING_LABEL_RADIUS = 10

class Inspector(object):

  def __init__(self):
    pygame.init()
    pygame.font.init()
    self.window_surface = pygame.display.set_mode((800, 600), 0, 32)
    self.frames = []
    self.font = pygame.font.SysFont('monospace', 10, bold=True)
    self.font_title = pygame.font.SysFont('monospace', 24, bold=True)

  def draw(self, cavern, stage, item):
    surface = pygame.Surface((800, 600))
    done = cavern.is_done()
    pygame.display.set_caption('A new cavern has been discovered!' if done else 'Speleogenesis...')
    x_offset = surface.get_width() / 2
    y_offset = surface.get_height() / 2
    scale = 4
    def sx(x):
      return scale * x + x_offset
    def sy(y):
      return scale * y + y_offset

    if not done:
      for space in cavern.spaces:
        color = space_color(space)
        if color is None:
          continue
        label_color = space_label_color(space)
        s_left = sx(space.left)
        s_top  = sy(space.top)
        pygame.draw.rect(surface, color, pygame.Rect(
          s_left,
          s_top,
          scale * space.width,
          scale * space.height))
        if isinstance(space, Bubble) and (
            scale * space.width < 20 or scale * space.height < 10):
          cx, cy = space.center
          theta = math.atan2(cy, cx)
          label_sx = 250 * math.cos(theta) + x_offset
          label_sy = 250 * math.sin(theta) + y_offset
          pygame.draw.line(
              surface,
              label_color,
              (label_sx, label_sy),
              (sx(cx), sy(cy))
          )
          pygame.draw.circle(
            surface,
            (0, 0, 0),
            (label_sx, label_sy),
            BUILDING_LABEL_RADIUS)
          pygame.draw.circle(
            surface,
            label_color,
            (label_sx, label_sy),
            BUILDING_LABEL_RADIUS,
            1)
          _draw_text(
              surface,
              self.font,
              f'{space.id:03d}',
              label_color,
              (label_sx, label_sy),
              (0, 0))
        else:
          _draw_text(
            surface,
            self.font,
            f'{space.id:03d}',
            label_color,
            (s_left, s_top),
            (1, 1))

      for path in cavern.paths:
        color = path_color(path)
        if color is None:
          continue
        for a, b in itertools.pairwise(path.baseplates):
          x1, y1 = a.center
          x2, y2 = b.center
          pygame.draw.line(
            surface,
            color,
            (sx(x1), sy(y1)),
            (sx(x2), sy(y2)),
            2)

    if cavern.diorama.bounds:
      left, top, width, height = cavern.diorama.bounds
      pygame.draw.rect(surface, Tile.SOLID_ROCK.inspect_color, pygame.Rect(
        sx(left),
        sy(top),
        scale * width,
        scale * height))

    for (x, y), tile in cavern.diorama.tiles.items():
      pygame.draw.rect(surface, tile.inspect_color, pygame.Rect(
        sx(x),
        sy(y),
        scale,
        scale))

    has_crystals = False
    for (x, y), crystals in cavern.diorama.crystals.items():
      has_crystals = True
      pygame.draw.circle(
        surface,
        CRYSTAL_COLOR,
        (sx(x + 0.5), sy(y + 0.5)),
        crystals,
        1)

    for building in cavern.diorama.buildings:
      cx = building.x + 0.5
      cy = building.y + 0.5
      theta = math.atan2(cy, cx)
      label_sx = 250 * math.cos(theta) + x_offset
      label_sy = 250 * math.sin(theta) + y_offset
      pygame.draw.line(
          surface,
          BUILDING_COLOR,
          (label_sx, label_sy),
          (sx(cx), sy(cy))
      )
      pygame.draw.circle(
        surface,
        (0, 0, 0),
        (label_sx, label_sy),
        BUILDING_LABEL_RADIUS)
      pygame.draw.circle(
        surface,
        BUILDING_COLOR,
        (label_sx, label_sy),
        BUILDING_LABEL_RADIUS,
        1)
      _draw_text(
          surface,
          self.font,
          building.type.inspect_abbrev,
          BUILDING_COLOR,
          (label_sx, label_sy),
          (0, 0))

    if not done:
      if cavern.diorama.bounds:
        left, top, width, height = cavern.diorama.bounds
        _draw_text(
            surface,
            self.font_title,
            str(width),
            TITLE_COLOR,
            (sx(left + width / 2), sy(top)),
            (0, 1))
        _draw_text(
            surface,
            self.font_title,
            str(height),
            TITLE_COLOR,
            (sx(left + width), sy(top + height / 2)),
            (-1, 0))
      
      for planner in cavern.planners:
        color = (0xff, 0xff, 0xff)

        bp_ct = len(planner.baseplates)

        if bp_ct == 1:
          cx, cy = planner.baseplates[0].center
          label_sx = sx(cx)
          label_sy = sy(cy)
        elif bp_ct == 2:
          cx1, cy1 = planner.baseplates[0].center
          cx2, cy2 = planner.baseplates[1].center
          label_sx = sx((cx1 + cx2) / 2)
          label_sy = sy((cy1 + cy2) / 2)
        elif bp_ct == 3:
          cx, cy = planner.baseplates[1].center
          label_sx = sx(cx)
          label_sy = sy(cy)
        else:
          cx = (min(bp.left   for bp in planner.baseplates)
              + max(bp.right  for bp in planner.baseplates)) / 2
          cy = (min(bp.top    for bp in planner.baseplates)
              + max(bp.bottom for bp in planner.baseplates)) / 2
          theta = math.atan2(cy, cx)
          
          label_sx = 250 * math.cos(theta) + x_offset
          label_sy = 250 * math.sin(theta) + y_offset
          mid_sx   = (label_sx + sx(cx) * (bp_ct - 1)) / bp_ct
          mid_sy   = (label_sy + sy(cy) * (bp_ct - 1)) / bp_ct

          pygame.draw.line(
            surface,
            color,
            (label_sx, label_sy),
            (mid_sx, mid_sy)
          )
          for bp in planner.baseplates:
            bp_x, bp_y = bp.center
            pygame.draw.line(
              surface,
              color,
              (mid_sx, mid_sy),
              (sx(bp_x), sy(bp_y))
            )
        
        bg_color = planner_bg_color(planner)
        if bg_color:
          pygame.draw.circle(
            surface,
            bg_color,
            (label_sx, label_sy),
            10)
        if (not has_crystals) and (planner.expected_crystals > 0):
          pygame.draw.circle(
            surface,
            CRYSTAL_COLOR,
            (label_sx, label_sy),
            scale / 2 + planner.expected_crystals,
            1)
        text = f'{planner.id}'
        _draw_text(
            surface,
            self.font,
            text,
            (0, 0, 0),
            (label_sx + 1, label_sy + 1),
            (0, 0))
        _draw_text(
            surface,
            self.font,
            text,
            color,
            (label_sx, label_sy),
            (0, 0))
          
    _draw_text(
        surface,
        self.font_title,
        f'{len(self.frames):4d} {stage}',
        TITLE_COLOR,
        (0, 0),
        (1, 1))
          
    _draw_text(
        surface,
        self.font_title,
        f'seed: {hex(cavern.context.seed)}',
        TITLE_COLOR,
        (surface.get_width(), 0),
        (-1, 1))

    crystals = (
      sum(cavern.diorama.crystals.values()) or
      sum(p.expected_crystals for p in cavern.planners)
    )
    if crystals > 0:
      _draw_text(
          surface,
          self.font_title,
          '%4d EC' % crystals,
          TITLE_COLOR,
          (0, surface.get_height()),
          (1, -1))

    self.frames.append((surface, stage))
    self.window_surface.blit(surface, (0, 0))
    pygame.display.flip()

  def wait(self):
    pygame.event.clear()
    last_surface = len(self.frames) - 1
    frame = last_surface
    def draw_frame():
      self.window_surface.fill((0, 0, 0))
      self.window_surface.blit(self.frames[frame][0], (0, 0))
      pygame.display.flip()
    try:
      while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
          return
        if event.type == pygame.KEYDOWN:
          if event.key in (pygame.K_LEFT, pygame.K_a):
            frame = max(frame - 1, 0)
          if event.key in (pygame.K_RIGHT, pygame.K_d):
            frame = min(frame + 1, last_surface)
          if event.key in (pygame.K_UP, pygame.K_w):
            stage = self.frames[frame][1]
            while frame > 0 and self.frames[frame][1] == stage:
              frame -= 1
              draw_frame()
          if event.key in (pygame.K_DOWN, pygame.K_s):
            if frame < last_surface:
              frame += 1
              draw_frame()
            stage = self.frames[frame][1]
            while frame < last_surface and self.frames[frame + 1][1] == stage:
              frame += 1
              draw_frame()
        draw_frame()
    except KeyboardInterrupt as e:
      pass

def _draw_text(
    surface, font, text: str, color: Tuple[int, int, int],
    pos: Tuple[float, float], gravity: Tuple[int, int]):
  lines = text.splitlines()
  gx, gy = gravity
  _, th = font.size('M')
  for i, line in enumerate(lines):
    font_surface = font.render(line, False, color)
    x, y = pos
    y += th * i
    if gx <= 0:
      x -= font_surface.get_width() * (0.5 if gx == 0 else 1)
    if gy <= 0:
      y -= th * len(lines) * (0.5 if gy == 0 else 1)
    surface.blit(
        font_surface,
        (x, y))

def space_color(space):
  if isinstance(space, Bubble):
    return BUBBLE_COLOR
  if isinstance(space, Baseplate):
    return BASEPLATE_COLORS[space.kind]

def space_label_color(space):
  if isinstance(space, Bubble):
    return BUBBLE_LABEL_COLOR
  if isinstance(space, Baseplate):
    return BASEPLATE_LABEL_COLOR

def path_color(path):
  return PATH_COLORS[path.kind]

def planner_bg_color(planner):
  if isinstance(planner, StemPlanner):
    if planner.fluid_type is None:
      return (0, 0, 0)
    return {
      StemPlanner.WATER: Tile.WATER.inspect_color,
      StemPlanner.LAVA: Tile.LAVA.inspect_color
    }[planner.fluid_type]
  return None