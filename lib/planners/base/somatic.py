import typing
from typing import Dict, Iterable, NamedTuple, Optional, Tuple

import abc
import collections
import functools
import itertools
import math

from .pearl import Oyster
from .planner import Planner
from lib.base import Rng
from lib.plastic import Diorama, Erosion, Landslide, Objective, Tile
from lib.utils.geometry import plot_line

PearlInfo = NamedTuple('PearlRow', pos=Tuple[int, int], layer=int, sequence=int)

class SomaticPlanner(Planner):

  def __init__(self, stem, oyster: Oyster):
    super().__init__(stem.id, stem.context)
    self._oyster = oyster
    self._pearl = None
    self._nacre = None
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
  def oyster(self) -> Oyster:
    return self._oyster

  @property
  def pearl(self) -> Optional[Tuple[PearlInfo]]:
    return self._pearl

  @functools.cached_property
  def expected_crystals(self) -> int:
    return self._get_expected_crystals()

  @abc.abstractmethod
  def _get_expected_crystals(self) -> int:
    pass

  @abc.abstractmethod
  def pearl_nucleus(self) -> Iterable[Tuple[int, int]]:
    pass

  def rough(self, tiles: Dict[Tuple[int, int], Tile]):
    self._pearl = tuple(self.walk_pearl(
        nucleus = self.pearl_nucleus(),
        max_layers = self.pearl_radius,
        baroqueness = self.baroqueness,
        rng = self.rng['rough.pearl']))
    self._nacre = self.oyster.create(self._pearl[-1].layer)
    for (x, y), layer, sequence in self._pearl:
      self._nacre.apply(tiles, (x, y), layer, sequence)

  @abc.abstractmethod
  def fine(self, diorama: Diorama):
    pass

  @abc.abstractmethod
  def script(self, diorama: Diorama):
    pass

  @property
  def objectives(self) -> Iterable[Objective]:
    return []

  def place_landslides(
      self,
      diorama: Diorama,
      total_frequency: float,
      pearl = None):
    rng = self.rng['fine.place_landslides']
    coverage = rng.uniform(min = 0.2, max = 0.8)
    if not pearl:
      pearl = self.pearl
    def h():
      for info in pearl:
        if (diorama.tiles.get(info.pos) in (
            Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK)
            and info.pos not in diorama.landslides
            and rng.chance(coverage)):
          yield info.pos
    positions = tuple(h())
    if positions:
      # Total activity is in total landslides per minute, but the file takes
      # delay seconds per landslide per tile.
      period = len(positions) * 60 / total_frequency
      event = Landslide(period)
      for pos in positions:
        diorama.landslides[pos] = event

  def fine_erosion(self, diorama: Diorama):
    if self.has_erosion:
      for info in self.pearl:
        if diorama.tiles.get(info.pos, Tile.SOLID_ROCK).passable_by_miner:
          diorama.erosions[info.pos] = Erosion.DEFAULT

  def walk_stream(self, baseplates=None):
    """Walks a contiguous 1-tile wide stream between contiguous baseplates."""
    log = self.context.logger.log_walk()
    if baseplates is None:
      baseplates = self.baseplates
    for a, b in itertools.pairwise(baseplates):
      x, y = a.center
      x = math.floor(x)
      y = math.floor(y)
      yield (x, y)
      log((x, y), 0)
      for (x1, y1), (x2, y2) in itertools.pairwise(plot_line((x, y), b.center)):
        if x1 != x2 and y1 != y2:
          yield x1, y2
          log((x1, y2), 0)
        yield x2, y2
        log((x2, y2), 0)

  def walk_pearl(
      self,
      nucleus: Iterable[Tuple[int, int]],
      max_layers: int,
      baroqueness: float,
      rng: Optional[Rng] = None,
      include_nucleus: bool = True) -> Iterable[PearlInfo]:
    log = self.context.logger.log_walk()
    if baroqueness and rng is None:
      raise AttributeError('Must supply rng when using baroqueness')
    last_layer = list(nucleus)
    if include_nucleus:
      for i, (x, y) in enumerate(last_layer):
        yield PearlInfo(pos=(x, y), layer=0, sequence=i)
    visited = {(x, y): (0, i) for i, (x, y) in enumerate(last_layer)}
    for layer_num in range(1, max_layers):
      this_layer = []
      # Starting at each point in the last layer,
      for x1, y1 in last_layer:
        done = False
        cx, cy, cvx, cvy = x1, y1, 0, 0
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
          cx, cy = (x1 + ox, y1 + oy)
          if (cx, cy) not in visited:
            cvx, cvy = -oy, ox
            break
        else:
          # Skip
          done = True
        # For each point the cursor visits,
        while not done:
          # Yield the cursor point.
          yield PearlInfo(
              pos=(cx, cy), layer=layer_num, sequence=len(this_layer))
          log((cx, cy), layer_num)
          visited[cx, cy] = (layer_num, len(this_layer))
          this_layer.append((cx, cy))
          # As it turns right, (vx, vy) as it turns right cycles between:
          # (1, 0) -> (0, 1) -> (-1, 0) -> (0, -1) -> ...
          # Try each of these possible movements:
          for vx, vy, ox, oy in (
              (-cvy,  cvx,    0,    0), # Right turn
              ( cvx,  cvy, -cvy,  cvx), # Straight, but drift right
              ( cvx,  cvy,    0,    0), # Straight
              ( cvx,  cvy,  cvy, -cvx), # Straight, but drift left
              ( cvy, -cvx,    0,    0), # Left turn
              ):
            # Find the next point
            nx, ny = cx + vx + ox, cy + vy + oy
            # If this point was visited,
            if (nx, ny) in visited:
              # ...during the current layer...
              visited_layer, visited_steps = visited[nx, ny]
              if (visited_layer == layer_num
                  # ...more than a few steps ago
                  and len(this_layer) > visited_steps + 4):
                # Finish exploring from this point.
                done = True
            # And the rng allows it...
            elif (
                not baroqueness
                or not typing.cast(Rng, rng).chance(baroqueness)):
              # Move to it
              cx, cy, cvx, cvy = nx, ny, vx, vy
              break
          # If no possible movement was acceptable,
          else:
            # Finish exploring this point.
            done = True
      last_layer = this_layer




