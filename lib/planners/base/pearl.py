from typing import Dict, Iterable

import itertools
import math

from lib.plastic import Tile

class Layer(object):

  def __init__(
      self,
      floor:      Tile = None,
      dirt:       Tile = None,
      loose_rock: Tile = None,
      hard_rock:  Tile = None,
      solid_rock: Tile = None,
      water:      Tile = None,
      lava:       Tile = None):
    self._data = {
      Tile.FLOOR : floor,
      Tile.DIRT : dirt,
      Tile.LOOSE_ROCK : loose_rock,
      Tile.HARD_ROCK : hard_rock,
      Tile.SOLID_ROCK : solid_rock,
      Tile.WATER : water,
      Tile.LAVA : lava,
    }

Layer.FLOOR = Layer(
    dirt       = Tile.FLOOR,
    loose_rock = Tile.FLOOR,
    hard_rock  = Tile.FLOOR,
    solid_rock = Tile.FLOOR,
    water      = Tile.FLOOR,
    lava       = Tile.FLOOR)
Layer.OPEN = Layer(
    dirt       = Tile.FLOOR,
    loose_rock = Tile.FLOOR,
    hard_rock  = Tile.FLOOR,
    solid_rock = Tile.FLOOR)
Layer.DIRT = Layer(
    floor      = Tile.DIRT,
    loose_rock = Tile.DIRT,
    hard_rock  = Tile.DIRT,
    solid_rock = Tile.DIRT)
Layer.LOOSE_ROCK = Layer(
    floor      = Tile.LOOSE_ROCK,
    dirt       = Tile.LOOSE_ROCK,
    hard_rock  = Tile.LOOSE_ROCK,
    solid_rock = Tile.LOOSE_ROCK)
Layer.HARD_ROCK = Layer(
    floor      = Tile.LOOSE_ROCK,
    solid_rock = Tile.HARD_ROCK)
Layer.WATER = Layer(
    floor      = Tile.WATER,
    dirt       = Tile.WATER,
    loose_rock = Tile.WATER,
    hard_rock  = Tile.WATER,
    solid_rock = Tile.WATER)
Layer.LAVA = Layer(
    floor      = Tile.LAVA,
    dirt       = Tile.LAVA,
    loose_rock = Tile.LAVA,
    hard_rock  = Tile.LAVA,
    solid_rock = Tile.LAVA)

class Oyster(object):

  def __init__(self, name: str):
    self._name = name
    self._layer_info = []
    self._width = 0
    self._shrink = 0
    self._grow = 0

  def __str__(self):
    return self._name

  def layer(self, layer: Layer, width=1, shrink=0, grow=0):
    self._layer_info.append((layer, width, shrink, grow))
    self._width += width
    self._shrink += shrink
    self._grow += grow
    return self

  def create(self, radius: int):

    radius = radius + 1

    grow_factor = 0
    shrink_factor = 0
    if radius < self._width and self._shrink:
      # For the shrink case,
      # r = (w0 * (1 - s0 * sf)) + (w1 * (1 - s1 * sf)) + ... + (wn * (1 - sn * sf))

      # Solve for sf
      # r = w0 - w0 * s0 * sf + w1 - w1 * s1 * sf + ... + wn - wn * sn * sf
      # r = (w0 + w1 + ... + wn) - (w0 * s0 + w1 * s1 + ... + wn * sn) * sf
      # (w0 * s0 + w1 * s1 + ... + wn * sn) * sf = (w0 + w1 + ... + wn) - r
      # sf = ((w0 + w1 + ... + wn) - r) / (w0 * s0 + w1 * s1 + ... + wn * sn)

      shrink_factor = (self._width - radius) / sum(
          width * shrink for _, width, shrink, _ in self._layer_info)

    elif radius > self._width and self._grow:
      # For the growth case,
      # r = (w0 + g0 * gf) + (w1 + g1 * gf) + ... + (wn + gn * gf)

      # Solve for gf
      # r = (w0 + w1 + ... + wn) + (g0 + g1 + ... + gn) * gf
      # (r - (w0 + w1 + ... + wn)) /  (g0 + g1 + ... + gn) = gf
      grow_factor = (radius - self._width) / self._grow
    def h():
      w = 0
      for layer, width, shrink, grow in self._layer_info:
        w = w + width * max(0, 1 - shrink * shrink_factor) + grow * grow_factor
        while round(w) > 0:
          yield layer
          w -= 1
    return Nacre(h())


class Nacre(object):

  def __init__(self, layers: Iterable[Layer]):
    self._layers = tuple(layers)
  
  def apply(self, pos, layer, tiles):
    if layer < len(self._layers):
      replace = tiles.get(pos, Tile.SOLID_ROCK)
      place = self._layers[layer]._data[replace]
      if place:
        tiles[pos] = place