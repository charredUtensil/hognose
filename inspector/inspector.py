from collections.abc import Callable
from typing import List, Optional, Tuple

import itertools
import math
import os
import queue
import threading
import traceback

from inspector.canvas import Canvas, FrozenCanvas, DrawContext, Fill, Rect
from inspector.infograph.common import OVERLAY_COLOR
from inspector.infograph.bsod import push_bsod
from inspector.infograph.state import push_state
from inspector.infograph.ui_overlay import UiOverlay
from lib import Cavern
from lib.base import Logger
from lib.plastic import Tile
from lib.planners import StemPlanner, SomaticPlanner
from lib.outlines import Baseplate, Path
from lib.version import VERSION

# Disable pygame's output on import
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame # pylint: disable=wrong-import-order,wrong-import-position

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
    push_state(canvas, cavern, details, self.warnings)
    self._push_frame(canvas.freeze())

  def log_warning(self, message: str):
    super().log_warning(message)
    self.warnings.append(message)
    self._notify_update()

  def log_exception(self, cavern: Cavern, e: Exception):
    try:
      self.log_state(cavern, -1, e)
    except Exception:
      super().log_warning('Failed to draw final state')
    super().log_exception(cavern, e)
    pygame.display.set_caption('Crashed :(')
    canvas = Canvas()
    push_bsod(canvas, cavern.context.seed, e)
    self._push_frame(canvas.freeze())

  def run(self):
    self._running = True
    pygame.init()
    pygame.font.init()
    window_surface = pygame.display.set_mode(
      (800, 600), pygame.RESIZABLE, 32)
    pygame.display.set_caption(f'Hognose {VERSION}')
    ui_overlay = UiOverlay()
    while self._running:
      self._draw(window_surface, ui_overlay)
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

  def _draw(self, window_surface, ui_overlay):
    if self.frames:
      dc = DrawContext(
          window_surface,
          self.scale,
          self.offset_x,
          self.offset_y)
      self.frames[self._frame_index].draw(dc)
      ui_overlay.update(
        index = self._frame_index,
        progress = self.progress,
        total = len(self.frames))
      ui_overlay.draw(dc)
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
      increment = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
      if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
          self._running = False
          return
        if event.key == pygame.K_LEFT:
          self._frame_index = max(self._frame_index - increment, 0)
        elif event.key == pygame.K_RIGHT:
          self._frame_index = min(self._frame_index + increment, len(self.frames) - 1)
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