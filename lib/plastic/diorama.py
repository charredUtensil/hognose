from collections.abc import Callable

import collections
import itertools
import math
import random
import time

class Diorama(object):
  def __init__(self):
    self._tiles = {}
    self._crystals = collections.Counter()
    self._ore = collections.Counter()
    self._buildings = []

  @property
  def tiles(self):
    return self._tiles

  @property
  def crystals(self):
    return self._crystals

  @property
  def ore(self):
    return self._ore

  @property
  def buildings(self):
    return self._buildings
