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

  def serialize(self):
    return serialize(self)