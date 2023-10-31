from typing import Dict, List, Optional, Tuple, Set

from collections.abc import Callable

import collections
import itertools
import math
import random
import time

from .building import Building
from .serialize import serialize
from .tile import Tile

class Diorama(object):
  def __init__(self, context):
    self.context = context

    self._tiles = {}
    self._crystals = collections.Counter()
    self._ore = collections.Counter()
    self._buildings = []
    self._open_cave_flags = set()
    self._discovered = set()
    self.camera_origin: Tuple[int, int] = (0, 0)
    self.bounds: Optional[Tuple[int, int, int, int]] = None

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
  def buildings(self) -> List[Building]:
    return self._buildings
  
  @property
  def open_cave_flags(self) -> Set[Tuple[int, int]]:
    return self._open_cave_flags

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
        for (ox, oy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
          if (x + ox, y + oy) not in self._discovered:
            queue.add((x + ox, y + oy))
            
  @property
  def discovered(self) -> Set[Tuple[int, int]]:
    return self._discovered

  def serialize(self):
    return serialize(self)