from typing import List, Tuple

import itertools
import math
import pygame
import traceback

from .frame import Frame, Absolute, Relative
from lib import Cavern
from lib.base import Logger
from lib.outlines import Bubble, Baseplate, Path
from lib.planners import StemPlanner
from lib.planners.caves import (
    EmptyCavePlanner,
    LostMinersCavePlanner,
    SpawnCavePlanner,
    TreasureCavePlanner)
from lib.planners.halls import (
    EmptyHallPlanner,
    ThinHallPlanner)
from lib.plastic import FindMinerObjective, ResourceObjective, Tile

TITLE_COLOR                            = (0x00, 0xff, 0x22)
LOG_ITEM_COLOR                         = (0xff, 0xff, 0xff)
WARNING_COLOR                          = (0xff, 0xff, 0x00)

BSOD_FG_COLOR                          = (0xff, 0xff, 0xff)
BSOD_BG_COLOR                          = (0x22, 0x22, 0xDD)

BUBBLE_OUTLINE_COLOR                   = (0x10, 0x00, 0x77)
BUBBLE_LABEL_COLOR_MOVING              = (0xff, 0xff, 0xff)
BUBBLE_LABEL_COLOR_STATIONARY          = (0x77, 0x77, 0xff)

BASEPLATE_COLORS = {
    Baseplate.AMBIGUOUS                : (0x20, 0x20, 0x20),
    Baseplate.EXCLUDED                 : None,
    Baseplate.SPECIAL                  : (0x77, 0x00, 0x10),
    Baseplate.HALL                     : (0x44, 0x00, 0x08),
}
BASEPLATE_OUTLINE_COLORS = {
    Baseplate.AMBIGUOUS                : (0x40, 0x40, 0x40),
    Baseplate.EXCLUDED                 : None,
    Baseplate.SPECIAL                  : None,
    Baseplate.HALL                     : None,
}
BASEPLATE_LABEL_COLORS = {
    Baseplate.AMBIGUOUS                : (0x77, 0x77, 0x77),
    Baseplate.EXCLUDED                 : None,
    Baseplate.SPECIAL                  : (0xff, 0x77, 0x77),
    Baseplate.HALL                     : None,
}

PATH_COLORS = {
    Path.AMBIGUOUS                     : (0x66, 0x66, 0x66),
    Path.EXCLUDED                      : None,
    Path.SPANNING                      : (0xff, 0xff, 0x00),
    Path.AUXILIARY                     : (0x44, 0xff, 0x00),
}

PLANNER_FLUID_COLORS = {
    None: Tile.FLOOR.inspect_color,
    Tile.WATER: Tile.WATER.inspect_color,
    Tile.LAVA: Tile.LAVA.inspect_color,
}
PLANNER_TYPE_BORDER_COLORS = {
    EmptyCavePlanner                   : (0xff, 0xff, 0xff),
    LostMinersCavePlanner              : (0xff, 0xff, 0x00),
    SpawnCavePlanner                   : (0x00, 0xff, 0xff),
    TreasureCavePlanner: Tile.CRYSTAL_SEAM.inspect_color,
    EmptyHallPlanner                   : (0x77, 0x00, 0x10),
    ThinHallPlanner                    : (0x77, 0x00, 0x10),
}
PLANNER_BORDER_COLOR = Tile.DIRT.inspect_color
PLANNER_TEXT_COLOR                     = (0xff, 0xff, 0xff)

PEARL_LAYER_COLORS = [
                                         (0xff, 0x00, 0xff),
                                         (0xff, 0xff, 0xff),
                                         (0xff, 0xff, 0x00),
                                         (0x00, 0xff, 0xff),
]
CRYSTAL_COLOR = Tile.CRYSTAL_SEAM.inspect_color
BUILDING_COLOR                          = (0xff, 0xff, 0x00)
BUILDING_LABEL_RADIUS = 10

MINER_COLOR                             = (0xff, 0xff, 0x00)

class Inspector(Logger):

  def __init__(self):
    pygame.init()
    pygame.font.init()
    self.window_surface = pygame.display.set_mode((800, 600), pygame.RESIZABLE, 32)
    self.frames: List[Tuple[Frame, str]] = []
    self.scale = 6
    self.font = pygame.font.SysFont('monospace', 10, bold=True)
    self.font_med = pygame.font.SysFont('trebuchetms', 16, bold=True)
    self.font_title = pygame.font.SysFont('trebuchetms', 24, bold=True)
    self.warnings = []

  def log(self, cavern: Cavern, stage, item):
    done = cavern.is_done()
    pygame.display.set_caption('A new cavern has been discovered!' if done else 'Speleogenesis...')
    
    frame = Frame()


    if cavern.diorama.bounds:
      # If there are bounds, draw solid rock in those bounds
      frame.draw_rect(
          Tile.SOLID_ROCK.inspect_color,
          cavern.diorama.bounds)
    else:
      # Draw bubbles and baseplates
      for b in cavern.baseplates:
        _draw_space(frame, b, BASEPLATE_COLORS[b.kind], BASEPLATE_OUTLINE_COLORS[b.kind])
      if stage in ('bubble', 'separate', 'rasterize'):
        for b in cavern.bubbles:
          _draw_space(frame, b, None, BUBBLE_OUTLINE_COLOR)
      if stage in ('bubble', 'separate'):
        for b in cavern.bubbles:
          color = (
            BUBBLE_LABEL_COLOR_MOVING if b.moving
            else BUBBLE_LABEL_COLOR_STATIONARY)
          _draw_space_label(frame, b, self.font, color)
      if not cavern.conquest:
        for b in cavern.baseplates:
          if b.kind == Baseplate.SPECIAL or stage in ('rasterize', 'discriminate'):
            _draw_space_label(frame, b, self.font,BASEPLATE_LABEL_COLORS[b.kind])

    # Draw paths
    if not cavern.conquest:
      for path in cavern.paths:
        color = PATH_COLORS[path.kind]
        if color is None:
          continue
        for a, b in itertools.pairwise(path.baseplates):
          frame.draw_line(
            color,
            a.center,
            b.center,
            3 if path.kind == Path.SPANNING else 2)

    # Draw circle markers for planners
    if stage in ('negotiate', 'flood', 'conquest'):
      for planner in cavern.conquest.planners:
        if isinstance(planner, StemPlanner):
          bg_color = PLANNER_FLUID_COLORS[planner.fluid_type]
          label_radius = 13 if planner.kind == StemPlanner.CAVE else 9
          _draw_planner(
              frame,
              planner,
              self.font,
              PLANNER_BORDER_COLOR,
              bg_color,
              label_radius)
    if stage in ('conquest', 'rough'):
      for planner in cavern.conquest.somatic_planners:
        if planner:
          bg_color = (0,0,0)
          border_color = PLANNER_TYPE_BORDER_COLORS[type(planner)]
          label_radius = 9
          _draw_planner(
              frame,
              planner,
              self.font,
              border_color,
              bg_color,
              label_radius)

    # Draw tiles
    for (x, y), tile in cavern.diorama.tiles.items():
      color = tile.inspect_color
      if stage == 'discover' and (x, y) not in cavern.diorama.discovered:
        c = sum(color) / 6
        color = (c, c, c)
      frame.draw_rect(color, (x, y, 1, 1))

    # Draw crystals
    for (x, y), crystals in cavern.diorama.crystals.items():
      if crystals < 5:
        frame.draw_circle(
          CRYSTAL_COLOR,
          (x + 0.5, y + 0.5),
          crystals / 4,
          1)
      else:
        frame.draw_label_for_rect(
          self.font,
          f'{crystals:d}',
          CRYSTAL_COLOR,
          (0, 0, 0),
          (x, y, 1, 1),
          (0, 0))

    # Draw buildings
    for building in cavern.diorama.buildings:
      frame.draw_label_for_rect(
        self.font,
        building.type.inspect_abbrev,
        BUILDING_COLOR,
        None,
        (building.x, building.y, 1, 1),
        (0, 0))

    # Draw miners
    for miner in cavern.diorama.miners:
      frame.draw_circle(
          MINER_COLOR,
          (miner.x, miner.y),
          0.25)

    # Draw objectives that have map positions
    for objective in cavern.diorama.objectives:
      if isinstance(objective, FindMinerObjective):
        frame.draw_circle(
            MINER_COLOR,
            (objective.miner.x, objective.miner.y),
            2,
            2)

    # Label height and width
    if stage == 'fence':
      if cavern.diorama.bounds:
        left, top, width, height = cavern.diorama.bounds
        label_rect = (left, top, width, height)
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

    # Draw titles
    frame.draw_text(
        self.font_title,
        f'{len(self.frames):4d} {stage}',
        TITLE_COLOR,
        (Relative(0), Relative(0)),
        (1, 1))
    frame.draw_text(
        self.font_title,
        f'seed: {hex(cavern.context.seed)}',
        TITLE_COLOR,
        (Relative(1), Relative(0)),
        (-1, 1))
    total_crystals = (
      cavern.diorama.total_crystals or
      sum(p.expected_crystals for p in cavern.planners)
    )
    if total_crystals > 0:
      goal_crystals = sum((
          o.crystals for o in cavern.diorama.objectives
          if isinstance(o, ResourceObjective)), 0)
      if goal_crystals:
        message = f'Collect {goal_crystals:d}/{total_crystals:d} EC'
      else:
        message = f'{total_crystals:d} EC'
      frame.draw_text(
          self.font_title,
          message,
          TITLE_COLOR,
          (Relative(0), Relative(1)),
          (1, -1))

    # Draw the log item
    if item:
      position = None
      frame.draw_text(
          self.font_med,
          str(item),
          LOG_ITEM_COLOR,
          (Relative(0.5), Relative(1)),
          (0, -1))
      if stage == 'rough':
        for ((x1, y1), l1, _), ((x2, y2), l2, _) in itertools.pairwise(item._pearl):
          if l1 > 0 and l1 == l2 and (x1 in range(x2-1,x2+2)) and (y1 in range(y2-1,y2+2)):
            frame.draw_line(
              PEARL_LAYER_COLORS[l1 % len(PEARL_LAYER_COLORS)],
              (x1 + 0.5, y1 + 0.5),
              (x2 + 0.5, y2 + 0.5),
              2)

    # Draw warnings since the last frame
    if self.warnings:
      frame.draw_text(
        self.font_med,
        '\n'.join(self.warnings),
        WARNING_COLOR,
        (Relative(1), Relative(1)),
        (-1, -1))
      self.warnings.clear()

    # Save the frame
    self.frames.append((frame, stage))
    self.draw_frame(frame)

  def log_warning(self, message: str):
    super().log_warning(message)
    self.warnings.append(message)

  def log_exception(self, cavern: Cavern, e: Exception):
    super().log_exception(cavern, e)
    pygame.display.set_caption('Crashed :(')
    frame = Frame()
    frame.fill(BSOD_BG_COLOR)
    frame.draw_text(
      self.font_title,
      f'{type(e).__name__} in {hex(cavern.context.seed)}',
      BSOD_FG_COLOR,
      (Relative(0), Relative(0.25)),
      (1, -1))
    frame.draw_text(
      self.font_med,
      ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
      BSOD_FG_COLOR,
      (Relative(0), Relative(0.25)),
      (1, 1))
    self.frames.append((frame, 'crash'))
    self.draw_frame(frame)

  def draw_frame(self, frame: Frame):
    self.window_surface.fill((0, 0, 0))
    frame.playback(self.window_surface, self.scale)
    pygame.display.flip()

  def wait(self):
    pygame.event.clear()
    last_index = len(self.frames) - 1
    index = last_index
    def draw():
      self.draw_frame(self.frames[index][0])
    try:
      while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
          return
        if event.type == pygame.KEYDOWN:
          if event.key in (pygame.K_ESCAPE, pygame.K_q):
            return
          elif event.key in (pygame.K_LEFT, pygame.K_a):
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
              stage = self.frames[index][1]
              while index > 0 and self.frames[index][1] == stage:
                index -= 1
                draw()
            else:
              index = max(index - 1, 0)
              draw()
          elif event.key in (pygame.K_RIGHT, pygame.K_d):
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
              if index < last_index:
                index += 1
                draw()
              stage = self.frames[index][1]
              while index < last_index and self.frames[index + 1][1] == stage:
                index += 1
                draw()
            else:
              index = min(index + 1, last_index)
              draw()
          elif event.key in (pygame.K_UP, pygame.K_w):
            self.scale = min(self.scale + 1, 10)
          elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.scale = max(self.scale - 1, 1)
        else:
          draw()
    except KeyboardInterrupt as e:
      pass

def _draw_space(frame, space, color, outline_color):
  rect = (
      space.left,
      space.top,
      space.width,
      space.height)
  if color:
    frame.draw_rect(color, rect)
  if outline_color:
    frame.draw_rect(outline_color, rect, 1)

def _draw_space_label(frame, space, font, color):
  if color:
    rect = (
        space.left,
        space.top,
        space.width,
        space.height)
    frame.draw_label_for_rect(
        font,
        f'{space.id:03d}',
        color,
        None,
        rect,
        (-1, -1))

def _draw_planner(frame, planner, font, border_color, bg_color, label_radius):
  origin = planner.center
  frame.draw_circle(
    border_color,
    origin,
    Absolute(label_radius + 2))
  for a, b in itertools.pairwise(planner.baseplates):
    frame.draw_line(
      border_color,
      a.center,
      b.center,
      7)
  frame.draw_circle(
    bg_color,
    origin,
    Absolute(label_radius))
  for a, b in itertools.pairwise(planner.baseplates):
    frame.draw_line(
      bg_color,
      a.center,
      b.center,
      3)
  if len(planner.baseplates) > 1:
    for i in 0, -1:
      frame.draw_circle(
        border_color,
        planner.baseplates[i].center,
        Absolute(4))
  frame.draw_text(
    font,
    f'{planner.id:d}',
    PLANNER_TEXT_COLOR,
    origin,
    (0, 0))