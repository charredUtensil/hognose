from typing import Iterable, Optional, Tuple

from lib.plastic import BasicTile, Tile


class Layer():
  """Rules for replacing tiles in a single layer of a Pearl."""

  def __init__( # pylint: disable=too-many-arguments
      self,
      floor: Optional[BasicTile] = None,
      dirt: Optional[BasicTile] = None,
      loose_rock: Optional[BasicTile] = None,
      hard_rock: Optional[BasicTile] = None,
      solid_rock: Optional[BasicTile] = None,
      water: Optional[BasicTile] = None,
      lava: Optional[BasicTile] = None):
    self._data = {
        Tile.FLOOR: floor,
        Tile.DIRT: dirt,
        Tile.LOOSE_ROCK: loose_rock,
        Tile.HARD_ROCK: hard_rock,
        Tile.SOLID_ROCK: solid_rock,
        Tile.WATER: water,
        Tile.LAVA: lava,
    }


# VOID: No effect whatsoever
Layer.VOID = Layer()

# ALWAYS_*: Ignores existing tile
def _always(tile: BasicTile):
  return Layer(
      floor=tile,
      dirt=tile,
      loose_rock=tile,
      hard_rock=tile,
      solid_rock=tile,
      water=tile,
      lava=tile)
Layer.ALWAYS_FLOOR = _always(Tile.FLOOR)
Layer.ALWAYS_DIRT = _always(Tile.DIRT)
Layer.ALWAYS_LOOSE_ROCK = _always(Tile.LOOSE_ROCK)
Layer.ALWAYS_HARD_ROCK = _always(Tile.HARD_ROCK)
Layer.ALWAYS_SOLID_ROCK = _always(Tile.SOLID_ROCK)
Layer.ALWAYS_WATER = _always(Tile.WATER)
Layer.ALWAYS_LAVA = _always(Tile.LAVA)

# AT_MOST_*: Replaces only if the existing tile is harder rock
Layer.AT_MOST_DIRT = Layer(
    loose_rock=Tile.DIRT,
    hard_rock=Tile.DIRT,
    solid_rock=Tile.DIRT)
Layer.AT_MOST_LOOSE_ROCK = Layer(
    hard_rock=Tile.LOOSE_ROCK,
    solid_rock=Tile.LOOSE_ROCK)
Layer.AT_MOST_HARD_ROCK = Layer(
    solid_rock=Tile.HARD_ROCK)

# No prefix: Replaces any non-flooded tile with the given tile
Layer.FLOOR = Layer(
    dirt=Tile.FLOOR,
    loose_rock=Tile.FLOOR,
    hard_rock=Tile.FLOOR,
    solid_rock=Tile.FLOOR)
Layer.DIRT = Layer(
    floor=Tile.DIRT,
    loose_rock=Tile.DIRT,
    hard_rock=Tile.DIRT,
    solid_rock=Tile.DIRT)
Layer.LOOSE_ROCK = Layer(
    floor=Tile.LOOSE_ROCK,
    dirt=Tile.LOOSE_ROCK,
    hard_rock=Tile.LOOSE_ROCK,
    solid_rock=Tile.LOOSE_ROCK)
Layer.HARD_ROCK = Layer(
    floor=Tile.HARD_ROCK,
    dirt=Tile.HARD_ROCK,
    loose_rock=Tile.HARD_ROCK,
    solid_rock=Tile.HARD_ROCK)
Layer.WATER = Layer(
    floor=Tile.WATER,
    dirt=Tile.WATER,
    loose_rock=Tile.WATER,
    hard_rock=Tile.WATER,
    solid_rock=Tile.WATER)
Layer.LAVA = Layer(
    floor=Tile.LAVA,
    dirt=Tile.LAVA,
    loose_rock=Tile.LAVA,
    hard_rock=Tile.LAVA,
    solid_rock=Tile.LAVA)

# Replaces floor -> dirt / loose rock <- hard rock, solid rock
Layer.DIRT_OR_LOOSE_ROCK = Layer(
    floor=Tile.DIRT,
    hard_rock=Tile.LOOSE_ROCK,
    solid_rock=Tile.LOOSE_ROCK)
# Replaces floor, dirt -> loose rock / hard rock <- solid rock
Layer.LOOSE_OR_HARD_ROCK = Layer(
    floor=Tile.LOOSE_ROCK,
    dirt=Tile.LOOSE_ROCK,
    solid_rock=Tile.HARD_ROCK)

# Bridges - Replaces placed rock with floor and floods solid rock
# This can be used by caves to create a path to an island.
# Avoid using these if the cave intersects halls with fluid as the results
# will look extremely strange.
Layer.BRIDGE_ON_WATER = Layer(
    dirt=Tile.FLOOR,
    loose_rock=Tile.FLOOR,
    hard_rock=Tile.FLOOR,
    solid_rock=Tile.WATER)
Layer.BRIDGE_ON_LAVA = Layer(
    dirt=Tile.FLOOR,
    loose_rock=Tile.FLOOR,
    hard_rock=Tile.FLOOR,
    solid_rock=Tile.LAVA)

# Solid becomes dirt, other rock becomes floor.
Layer.INVERT_TO_DIRT = Layer(
    dirt=Tile.FLOOR,
    loose_rock=Tile.FLOOR,
    hard_rock=Tile.FLOOR,
    solid_rock=Tile.DIRT)
# Solid becomes loose rock, other rock becomes floor.
Layer.INVERT_TO_LOOSE_ROCK = Layer(
    dirt=Tile.FLOOR,
    loose_rock=Tile.FLOOR,
    hard_rock=Tile.FLOOR,
    solid_rock=Tile.LOOSE_ROCK)


class Oyster():
  """A Pearl Factory."""

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
      # r = (w0 * (1 - s0 * sf)) + (w1 * (1 - s1 * sf)) + ...
      #     + (wn * (1 - sn * sf))

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
    return Pearl(radius, h())


class PearlTile():
  def __init__(self, pos, layer, sequence):
    self.pos: Tuple[int, int] = pos
    self.layer: int = layer
    self.sequence: int = sequence


class Pearl():
  """An object describing the tiles used in a Planner."""

  def __init__(self, radius: int, layers: Iterable[Layer]):
    self._radius = radius
    self._layers = tuple(layers)
    self._infos = []
    self._by_pos = {}

  def mark(self, pos, layer):
    if self._infos and layer == self._infos[-1].layer:
      sequence = self._infos[-1].sequence + 1
    else:
      sequence = 0
    pt = PearlTile(pos, layer, sequence)
    self._infos.append(pt)
    self._by_pos[pos] = pt

  @property
  def nucleus(self) -> Iterable[PearlTile]:
    for info in self._infos:
      if info.layer > 0:
        break
      yield info

  @property
  def inner(self) -> Iterable[PearlTile]:
    for info in self._infos:
      if info.layer >= self._radius:
        break
      yield info

  @property
  def outer(self) -> Iterable[PearlTile]:
    for info in self._infos:
      if info.layer >= self._radius:
        yield info

  def __contains__(self, pos: Tuple[int, int]):
    return pos in self._by_pos

  def __getitem__(self, pos: Tuple[int, int]):
    return self._by_pos[pos]
