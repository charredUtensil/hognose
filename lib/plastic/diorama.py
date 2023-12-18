from typing import Dict, List, Optional, Tuple, Type, Set

from collections.abc import Callable

import collections
import itertools
import math
import random
import time

from .building import Building
from .creatures import Creature
from .hazards import Erosion, Landslide
from .miners import Miner
from .objectives import Objective
from .position import Position
from .serialize import serialize
from .scripts import Script
from .tile import Tile

class Diorama(object):
  def __init__(self, context):
    self.context = context

    # Tile-indexed
    self._tiles = {}
    self._crystals = collections.Counter()
    self._ore = collections.Counter()
    self._landslides = {}
    self._erosions = {}

    self._discovered = set()
    self._in_play = set()
    self._open_cave_flags = set()

    # Entities with positions
    self._buildings = []
    self._miner_ids = itertools.count()
    self._miners = []
    self._creature_ids = itertools.count()
    self._creatures = []
    self._script = Script()
    self.camera_position: Position = (
        Position((0, 0, 0), (math.pi / 4, 0, 0)))

    # Non-positional items
    self._objectives = []
    self.briefing: str = ''
    self.briefing_success: str = ''
    self.briefing_failure: str = ''
    self.level_name: str = ''

    self.bounds: Optional[Tuple[int, int, int, int]] = None

  # Tile-indexed
  @property
  def tiles(self) -> Dict[Tuple[int, int], Tile]:
    return self._tiles

  @property
  def crystals(self) -> Dict[Tuple[int, int], int]:
    return self._crystals

  @property
  def ore(self) -> Dict[Tuple[int, int], int]:
    return self._ore

  @property
  def landslides(self) -> Dict[Tuple[int, int], Landslide]:
    return self._landslides

  @property
  def erosions(self) -> Dict[Tuple[int, int], Erosion]:
    return self._erosions
  
  @property
  def discovered(self) -> Set[Tuple[int, int]]:
    return self._discovered

  @property
  def in_play(self) -> Set[Tuple[int, int]]:
    return self._in_play

  @property
  def open_cave_flags(self) -> Set[Tuple[int, int]]:
    return self._open_cave_flags

  # Entities with positions
  @property
  def buildings(self) -> List[Building]:
    return self._buildings

  def miner(self, *args, **kwargs) -> Miner:
    m = Miner(next(self._miner_ids), *args, **kwargs)
    self._miners.append(m)
    return m

  @property
  def miners(self) -> List[Miner]:
    return self._miners

  def creature(self, *args, **kwargs) -> Creature:
    c = Creature(next(self._creature_ids), *args, **kwargs)
    self._creatures.append(c)
    return c

  @property
  def creatures(self) -> List[Creature]:
    return self._creatures

  @property
  def script(self) -> Script:
    return self._script

  # Non-positional items and helpers

  @property
  def objectives(self) -> List[Objective]:
    return self._objectives

  @property
  def total_crystals(self) -> int:
    return (
      sum(self._crystals.values())
      + sum(4 for t in self._tiles.values() if t == Tile.CRYSTAL_SEAM)
    )

  def discover(self):
    queue = set(self._open_cave_flags)
    while queue:
      x, y = queue.pop()
      if not self._tiles.get((x, y), Tile.SOLID_ROCK).is_wall:
        self._discovered.add((x, y))
        for ox in (-1, 0, 1):
          for oy in (-1, 0, 1):
            if (x + ox, y + oy) not in self._discovered:
              queue.add((x + ox, y + oy))

  def wander(self):
    queue = [next(pos for pos, tile in self._tiles.items() if tile == Tile.FLOOR)]
    queue.append(None)
    stale = True
    while True:
      if queue[0] is None:
        if stale:
          return
        else:
          stale = True
          queue.pop(0)
          queue.append(None)
          continue
      x, y = queue.pop(0)
      if (self._tiles.get((x, y), Tile.SOLID_ROCK)
          not in (Tile.SOLID_ROCK, Tile.RECHARGE_SEAM)):
        pass
      elif (x - 1, y) in self._in_play and (x + 1, y) in self._in_play:
        pass
      elif (x, y - 1) in self._in_play and (x, y + 1) in self._in_play:
        pass
      else:
        queue.append((x, y))
        continue
      stale = False
      self._in_play.add((x, y))
      for ox, oy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        neighbor = (x + ox, y + oy)
        if (neighbor not in self._in_play
            and neighbor not in queue):
          queue.append(neighbor)

  def serialize(self):
    return serialize(self)