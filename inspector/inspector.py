from collections.abc import Callable
from typing import List, Optional, Tuple

import itertools
import math
import os
import queue
import threading
import traceback

from inspector.canvas import Canvas, FrozenCanvas, DrawContext, Fill, Rect
from inspector.infograph.common import Z_BACKGROUND, Z_BOUNDS
from inspector.infograph.bsod import push_bsod
from inspector.infograph.map import push_map
from inspector.infograph.outlines import push_outlines
from inspector.infograph.overlays import OVERLAY_COLOR, push_overlays
from inspector.infograph.planners import push_planners
from lib import Cavern
from lib.base import Logger
from lib.plastic import Tile
from lib.planners import StemPlanner, SomaticPlanner
from lib.outlines import Baseplate, Path
from lib.version import VERSION

# Disable pygame's output on import
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame # pylint: disable=wrong-import-order,wrong-import-position


PROGRESS_COLOR = OVERLAY_COLOR

UPDATE_REQUESTED = pygame.event.Event(pygame.event.custom_type())


class Inspector(Logger):

  def __init__(self, verbosity):
    super().__init__()
    self.frames: List[FrozenCanvas] = []
    self._frame_index = 0
    self.progress: float = 0
    self.scale = 6
    self.offset_x = 0
    self.offset_y = 0
    self.warnings = []
    self.verbosity = verbosity
    self._running = False

  def log_progress(self, progress):
    self.progress = progress

  def log_state(self, cavern, verbosity, details):
    if verbosity > self.verbosity:
      return
    canvas = Canvas()
    canvas.push(Fill(color=(0, 0, 0)), Z_BACKGROUND)
    if cavern.conquest:
      push_planners(canvas, cavern.conquest.planners)
    else:
      push_outlines(canvas, cavern.bubbles, cavern.baseplates, cavern.paths)
    push_map(canvas, cavern.diorama)
    push_overlays(canvas, cavern, self.warnings)
    self._push_frame(canvas.freeze())

  def log_warning(self, message: str):
    super().log_warning(message)
    self.warnings.append(message)
    self._notify_update()

  def log_exception(self, cavern: Cavern, e: Exception):
    try:
      self.log_state(cavern, -1)
    except Exception:
      super().log_warning('Failed to draw final state')
    super().log_exception(e)
    pygame.display.set_caption('Crashed :(')
    canvas = Canvas()
    push_bsod(canvas, cavern.context.seed, e)
    self._push_frame(canvas.freeze())

  def run(self):
    self._running = True
    pygame.init()
    pygame.font.init()
    self.window_surface = pygame.display.set_mode(
      (800, 600), pygame.RESIZABLE, 32)
    pygame.display.set_caption(f'Hognose {VERSION}')
    while self._running:
      self._draw()
      self._input()

  def _notify_update(self):
    try:
      pygame.event.post(UPDATE_REQUESTED)
    except pygame.error:
      pass

  def _push_frame(self, frame: FrozenCanvas):
    self.frames.append(frame)
    if self._frame_index == len(self.frames) - 2:
      self._frame_index += 1
    self._notify_update()

  def _draw_progress_bar(self):
    ox = self.window_surface.get_width() // 2
    oy = self.window_surface.get_height() // 2
    w = 400
    h = 20
    pygame.draw.rect(
      self.window_surface,
      PROGRESS_COLOR,
      pygame.Rect(ox - w // 2, oy - h // 2, w * self.progress, h))
    pygame.draw.rect(
      self.window_surface,
      PROGRESS_COLOR,
      pygame.Rect(ox - w // 2, oy - h // 2, w, h),
      2)

  def _draw(self):
    if self.frames:
      dc = DrawContext(
          self.window_surface,
          self.scale,
          self.offset_x,
          self.offset_y)
      self.frames[self._frame_index].draw(dc)
      if self.progress < 1:
        self._draw_progress_bar()
      pygame.display.flip()

  def _input(self):
    def events():
      yield pygame.event.wait()
      while True:
        event = pygame.event.poll()
        if event.type == pygame.NOEVENT:
          return
        yield event
    for event in events():
      if event.type == pygame.QUIT:
        self._running = False
        return
      if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
          self._running = False
          return
        if event.key == pygame.K_LEFT:
          self._frame_index = max(self._frame_index - 1, 0)
        elif event.key == pygame.K_RIGHT:
          self._frame_index = min(self._frame_index + 1, len(self.frames) - 1)
        elif event.key == pygame.K_UP:
          self.scale = min(self.scale + 1, 20)
        elif event.key == pygame.K_DOWN:
          self.scale = max(self.scale - 1, 1)
        elif event.key == pygame.K_w:
          self.offset_y += 1
        elif event.key == pygame.K_a:
          self.offset_x += 1
        elif event.key == pygame.K_s:
          self.offset_y -= 1
        elif event.key == pygame.K_d:
          self.offset_x -= 1