import typing
from typing import Dict, Iterable, NamedTuple, Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
  from lib.lore import Lore

import abc
import collections
import functools
import itertools
import math

from .pearl import Oyster, Pearl
from .planner import Planner
from lib.base import Rng
from lib.holistics import Adjurator
from lib.plastic import Diorama, Erosion, Landslide, Tile

class SomaticPlanner(Planner):

  def __init__(self, stem, oyster: Oyster):
    super().__init__(stem.id, stem.context)
    self._oyster = oyster
    self._pearl = None
    self._stem = stem

  @property
  @abc.abstractmethod
  def baroqueness(self) -> float:
    pass

  @property
  def baseplates(self):
    return self._stem.baseplates

  @property
  def fluid_type(self):
    return self._stem.fluid_type

  @property
  def has_erosion(self):
    return self._stem.has_erosion

  @property
  @abc.abstractmethod
  def inspect_color(self) -> Tuple[int, int, int]:
    pass

  @property
  def oyster(self) -> Oyster:
    return self._oyster

  @property
  def pearl(self) -> Optional[Pearl]:
    return self._pearl

  @functools.cached_property
  def expected_crystals(self) -> int:
    return self._get_expected_crystals()

  @abc.abstractmethod
  def _get_expected_crystals(self) -> int:
    pass

  def rough(self, tiles: Dict[Tuple[int, int], Tile]):
    self._pearl = self.oyster.create(self.pearl_radius)
    self.build_pearl()
    for pt in self._pearl.inner:
      if pt.layer < len(self._pearl._layers):
        replace = tiles.get(pt.pos, Tile.SOLID_ROCK)
        place = self._pearl._layers[pt.layer]._data[replace]
        if place:
          tiles[pt.pos] = place

  @abc.abstractmethod
  def fine(self, diorama: Diorama):
    pass

  @abc.abstractmethod
  def script(self, diorama: Diorama, lore: 'Lore'):
    pass

  def adjure(self, adjurator: Adjurator):
    pass

  def place_landslides(
      self,
      diorama: Diorama,
      total_frequency: float,
      pearl: Optional[Pearl] = None):
    rng = self.rng['fine.place_landslides']
    coverage = rng.uniform(min = 0.2, max = 0.8)
    if not pearl:
      pearl = self.pearl
    def h():
      for info in typing.cast(Pearl, pearl).inner:
        if (diorama.tiles.get(info.pos) in (
            Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK)
            and info.pos not in diorama.landslides
            and rng.chance(coverage)):
          yield info.pos
    positions = tuple(h())
    if positions:
      # Total frequency is in total landslides per minute, but the file takes
      # delay seconds per landslide per tile.
      period = max(
          len(positions) * 60 / total_frequency,
          self.context.min_landslide_period)
      event = Landslide(period)
      for pos in positions:
        diorama.landslides[pos] = event

  def fine_erosion(self, diorama: Diorama):
    if self.has_erosion:
      for info in typing.cast(Pearl, self.pearl).inner:
        if diorama.tiles.get(info.pos, Tile.SOLID_ROCK).passable_by_miner:
          diorama.erosions[info.pos] = Erosion.DEFAULT

  @property
  def pearl_radius(self):
    return self._stem.pearl_radius
    
  @abc.abstractmethod
  def make_nucleus(self) -> Dict[int, Iterable[Tuple[int, int]]]:
    pass

  def build_pearl(self):
    rng = self.rng['rough.pearl']
    nucleus = self.make_nucleus()
    last_layer = []
    for layer_num in range(0, self.pearl_radius + 4):
      this_layer = []
      # Add tiles from nucleus
      for x, y in nucleus.get(layer_num, []):
        if (x, y) not in self._pearl:
          self._pearl.mark(pos=(x, y), layer=layer_num)
          this_layer.append((x, y))
      queue = []
      # Starting at each point in the last layer,
      for x, y in last_layer:
        # Push all adjacent tiles onto the queue.
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
          nx, ny = (x + ox, y + oy)
          if (nx, ny) not in self._pearl:
            queue.append((nx, ny, -oy, ox))
      while queue:
        x, y, vx, vy = queue.pop(0)
        if (x, y) in self._pearl:
          continue
        # Mark the cursor point.
        self._pearl.mark(pos=(x, y), layer=layer_num)
        this_layer.append((x, y))
        # As it turns right, (vx, vy) as it turns right cycles between:
        # (1, 0) -> (0, 1) -> (-1, 0) -> (0, -1) -> ...
        # Try each of these possible movements:
        offsets = (
          (  0,   0, -vy,  vx), # Right turn
          (-vy,  vx,  vx,  vy), # Straight, but drift right
          (  0,   0,  vx,  vy), # Straight
          ( vy, -vx,  vx,  vy), # Straight, but drift left
          (  0,   0,  vy, -vx), # Left turn
        )
        next_points = tuple(
            (x + ox + vx, y + oy + vy, vx, vy)
            for ox, oy, vx, vy in offsets
        )

        def is_enclosed():
          for nx, ny, _, _ in next_points:
            if (nx, ny) not in self._pearl:
              continue
            info = self._pearl[nx, ny]
            if info.layer == layer_num and info.sequence + 4 < len(this_layer):
              return True
          return False
        if not is_enclosed():
          for nx, ny, nvx, nvy in next_points:
            # If the point was not visited and the rng allows it
            if (nx, ny) in self._pearl:
              continue
            if (layer_num > self.pearl_radius
                or not rng.chance(self.baroqueness)):
              # Push it to the queue and don't check any other movements.
              queue.insert(0, (nx, ny, nvx, nvy))
              break
      last_layer = this_layer




