from typing import Iterable

import itertools
import math

from lib.plastic import Tile

class Layer(object):

  def __init__(self, place: Tile):
    self._place = place

Layer.WATER = Layer(Tile.WATER)
Layer.LAVA = Layer(Tile.LAVA)
Layer.FLOOR = Layer(Tile.FLOOR)
Layer.DIRT = Layer(Tile.DIRT)
Layer.LOOSE_ROCK = Layer(Tile.LOOSE_ROCK)
Layer.HARD_ROCK = Layer(Tile.HARD_ROCK)

class Oyster(object):

  def __init__(self):
    self._layer_info = []
    self._width = 0
    self._shrink = 0
    self._grow = 0

  def layer(self, layer: Layer, width=1, shrink=0, grow=0):
    self._layer_info.append((layer, width, shrink, grow))
    self._width += width
    self._shrink += shrink
    self._grow += grow
    return self

  def create(self, radius: int):
    if radius <= self._width:
      s = (radius - self._width) / self._shrink if self._shrink else 0
      n = []
      c = 0
      for (layer, width, shrink, _) in self._layer_info:
        x = max(c, c + width - shrink * s)
        for _ in range(round(c), round(x) + 1):
          n.append(layer)
        c = x
      return Nacre(n)
    else:
      g = (radius - self._width) / self._grow if self._grow else 0
      n = []
      c = 0
      for (layer, width, _, grow) in self._layer_info:
        x = c + width + grow * g
        for _ in range(round(c), round(x) + 1):
          n.append(layer)
        c = x
      return Nacre(n)

class Nacre(object):

  def __init__(self, layers: Iterable[Layer]):
    self._layers = tuple(layers)
  
  def apply(self, pos, layer, tiles):
    if layer < len(self._layers):
      tiles[pos] = self._layers[layer]._place