from typing import Tuple

import itertools
import math
import pygame

from .frame import Frame, RelativeScreenCoord
from lib.outlines import Bubble, Baseplate, Path
from lib.planners import StemPlanner
from lib.plastic import Tile

TITLE_COLOR            = (0x00, 0xff, 0x22)
BUBBLE_COLOR           = (0x08, 0x00, 0x44)
BUBBLE_OUTLINE_COLOR   = (0x10, 0x00, 0x77)
BUBBLE_LABEL_COLOR     = (0xff, 0xff, 0xff)
BASEPLATE_COLORS = {
  Baseplate.AMBIGUOUS  : (0x40, 0x40, 0x40),
  Baseplate.EXCLUDED   : None,
  Baseplate.SPECIAL    : (0x77, 0x00, 0x10),
  Baseplate.HALL       : (0x44, 0x00, 0x08),
}
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
    self.frames: List[Tuple[Frame, str]] = []
    self.scale = 5
    self.font = pygame.font.SysFont('monospace', 10, bold=True)
    self.font_title = pygame.font.SysFont('monospace', 24, bold=True)

  def draw(self, cavern, stage, item):
    done = cavern.is_done()
    pygame.display.set_caption('A new cavern has been discovered!' if done else 'Speleogenesis...')
    
    frame = Frame()

    if not done:
      for first in (True, False):
        for space in cavern.spaces:
          color, outline_color, label_color = space_colors(space)
          if color is None:
            continue
          space_rect = pygame.Rect(
              space.left,
              space.top,
              space.width,
              space.height)
          if first:
            frame.draw_rect(color, space_rect)
            if outline_color:
              frame.draw_rect(outline_color, space_rect, 1)
          else:
            if label_color:
              frame.draw_label_for_rect(
                  self.font,
                  f'{space.id:03d}',
                  label_color,
                  None,
                  space_rect,
                  (-1, -1))

      for path in cavern.paths:
        color = path_color(path)
        if color is None:
          continue
        for a, b in itertools.pairwise(path.baseplates):
          frame.draw_line(
            color,
            a.center,
            b.center,
            2)

    if cavern.diorama.bounds:
      frame.draw_rect(
          Tile.SOLID_ROCK.inspect_color,
          pygame.Rect(*cavern.diorama.bounds))

    for (x, y), tile in cavern.diorama.tiles.items():
      frame.draw_rect(tile.inspect_color, pygame.Rect(x, y, 1, 1))

    has_crystals = False
    for (x, y), crystals in cavern.diorama.crystals.items():
      has_crystals = True
      frame.draw_circle(
        CRYSTAL_COLOR,
        (x + 0.5, y + 0.5),
        crystals / 3,
        1)

    for building in cavern.diorama.buildings:
      frame.draw_label_for_rect(
        self.font,
        building.type.inspect_abbrev,
        BUILDING_COLOR,
        None,
        pygame.Rect(building.x, building.y, 1, 1),
        (0, 0))

    if not done:
      if cavern.diorama.bounds:
        left, top, width, height = cavern.diorama.bounds
        label_rect = pygame.Rect(left, top, width, height)
        frame.draw_label_for_rect(
            self.font_title,
            str(width),
            TITLE_COLOR,
            None,
            label_rect,
            (0, -1))
        frame.draw_label_for_rect(
            self.font_title,
            str(height),
            TITLE_COLOR,
            None,
            label_rect,
            (1, 0))
      
      for planner in cavern.planners:
        fg_color = (0xff, 0xff, 0xff)
        bp_ct = len(planner.baseplates)
        if bp_ct == 1:
          origin = planner.baseplates[0].center
        elif bp_ct == 2:
          cx1, cy1 = planner.baseplates[0].center
          cx2, cy2 = planner.baseplates[1].center
          origin = (cx1 + cx2) / 2, (cy1 + cy2) / 2
        elif bp_ct == 3:
          origin = planner.baseplates[1].center
        else:
          pass
        bg_color = planner_bg_color(planner)
        if bg_color:
          frame.draw_circle(
            bg_color,
            origin,
            10)
        frame.draw_text(
          self.font,
          str(planner.id),
          fg_color,
          origin,
          (0, 0))
        if (not has_crystals) and (planner.expected_crystals > 0):
          frame.draw_circle(
            CRYSTAL_COLOR,
            origin,
            planner.expected_crystals / 3,
            1)
         
    frame.draw_text(
        self.font_title,
        f'{len(self.frames):4d} {stage}',
        TITLE_COLOR,
        (RelativeScreenCoord(0), RelativeScreenCoord(0)),
        (1, 1))
          
    frame.draw_text(
        self.font_title,
        f'seed: {hex(cavern.context.seed)}',
        TITLE_COLOR,
        (RelativeScreenCoord(1), RelativeScreenCoord(0)),
        (-1, 1))

    crystals = (
      sum(cavern.diorama.crystals.values()) or
      sum(p.expected_crystals for p in cavern.planners)
    )
    if crystals > 0:
      frame.draw_text(
          self.font_title,
          '%4d EC' % crystals,
          TITLE_COLOR,
          (RelativeScreenCoord(0), RelativeScreenCoord(1)),
          (1, -1))

    self.frames.append((frame, stage))
    self.draw_frame(frame)

  def draw_frame(self, frame: Frame):
    self.window_surface.fill((0, 0, 0))
    frame.playback(self.window_surface, self.scale)
    pygame.display.flip()

  def wait(self):
    pygame.event.clear()
    last_index = len(self.frames) - 1
    index = last_index
    try:
      while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
          return
        if event.type == pygame.KEYDOWN:
          if event.key in (pygame.K_LEFT, pygame.K_a):
            index = max(index - 1, 0)
          if event.key in (pygame.K_RIGHT, pygame.K_d):
            index = min(index + 1, last_index)
          if event.key in (pygame.K_UP, pygame.K_w):
            stage = self.frames[index][1]
            while index > 0 and self.frames[index][1] == stage:
              index -= 1
              self.draw_frame(self.frames[index][0])
          if event.key in (pygame.K_DOWN, pygame.K_s):
            if index < last_index:
              index += 1
              self.draw_frame(self.frames[index][0])
            stage = self.frames[index][1]
            while index < last_index and self.frames[index + 1][1] == stage:
              index += 1
              self.draw_frame(self.frames[index][0])
        self.draw_frame(self.frames[index][0])
    except KeyboardInterrupt as e:
      pass

def space_colors(space):
  if isinstance(space, Bubble):
    return BUBBLE_COLOR, BUBBLE_OUTLINE_COLOR, BUBBLE_LABEL_COLOR
  if isinstance(space, Baseplate):
    return BASEPLATE_COLORS[space.kind], None, None

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