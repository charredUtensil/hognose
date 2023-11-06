from typing import Dict, Iterable, NamedTuple, Optional, Tuple
import abc
import collections
import itertools
import math

from .pearl import Oyster
from .planner import Planner
from lib.plastic import Diorama, Objective, Tile
from lib.utils.geometry import plot_line

PearlInfo = NamedTuple('PearlRow', pos=Tuple[int, int], layer=int, sequence=int)

class SomaticPlanner(Planner):

  def __init__(self, stem, oyster: Oyster):
    super().__init__(stem.id, stem.context, stem.baseplates)
    self._oyster = oyster
    self._pearl = None

  @property
  @abc.abstractmethod
  def baroqueness(self) -> float:
    pass

  @property
  def oyster(self) -> Oyster:
    return self._oyster

  @property
  def pearl(self) -> Optional[Tuple[PearlInfo]]:
    return self._pearl

  @abc.abstractmethod
  def pearl_nucleus(self) -> Iterable[Tuple[int, int]]:
    pass

  def rough(self, tiles: Dict[Tuple[int, int], Tile]):
    self._pearl = tuple(self.walk_pearl(
        nucleus = self.pearl_nucleus(),
        max_layers = self.pearl_radius,
        baroqueness = self.baroqueness))
    nacre = self.oyster.create(self._pearl[-1].layer)
    for (x, y), layer, sequence in self._pearl:
      nacre.apply(tiles, (x, y), layer, sequence)

  @abc.abstractmethod
  def fine(self, diorama: Diorama):
    pass

  @property
  def objectives(self) -> Iterable[Objective]:
    return []

  def walk_stream(self, baseplates=None):
    """Walks a contiguous 1-tile wide stream between contiguous baseplates."""
    if baseplates is None:
      baseplates = self.baseplates
    for a, b in itertools.pairwise(baseplates):
      for (x1, y1), (x2, y2) in itertools.pairwise(plot_line(a.center, b.center)):
        yield x2, y2
        if x1 != x2 and y1 != y2:
          yield x1, y2

  def walk_pearl(
      self,
      nucleus: Iterable[Tuple[int, int]],
      max_layers: int,
      baroqueness: float,
      include_nucleus: bool = True) -> Iterable[PearlInfo]:
    last_layer = list(nucleus)
    for i, (x, y) in enumerate(last_layer):
      yield PearlInfo(pos=(x, y), layer=0, sequence=i)
    visited = {(x, y): (0, i) for i, (x, y) in enumerate(last_layer)}
    for layer_num in range(1, max_layers):
      this_layer = []
      # Starting at each point in the last layer,
      for x1, y1 in last_layer:
        done = False
        if (x1, y1 - 1) not in visited:
          # Put the cursor at the point north of it facing east.
          cx, cy, cvx, cvy = x1, y1 - 1, 1, 0
        elif (x1, y1 + 1) not in visited:
          # Put the cursor at the point south of it facing west.
          cx, cy, cvx, cvy = x1, y1 + 1, -1, 0
        else:
          # Skip
          done = True
        # For each point the cursor visits,
        while not done:
          # Yield the cursor point.
          yield PearlInfo(
              pos=(cx, cy), layer=layer_num, sequence=len(this_layer))
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
                or self.rng.random() > baroqueness):
              # Move to it
              cx, cy, cvx, cvy = nx, ny, vx, vy
              break
          # If no possible movement was acceptable,
          else:
            # Finish exploring this point.
            done = True
      last_layer = this_layer




