from typing import Dict, Iterable, Optional, Tuple

import abc
import collections
import itertools
import math

from .planner import Planner
from lib.planners.onions import Onion
from lib.plastic import Diorama, Tile
from lib.utils.geometry import plot_line

class SomaticPlanner(Planner):

  def __init__(self, stem):
    super().__init__(stem.id, stem.context, stem.baseplates)
    self.onion: Optional[Onion] = None

  @abc.abstractmethod
  def rough(self, tiles: Dict[Tuple[int, int], Tile]):
    pass

  @abc.abstractmethod
  def fine(self, diorama: Diorama):
    pass

  def walk_stream(self, baseplates=None):
    """Walks a contiguous 1-tile wide stream between contiguous baseplates."""
    if baseplates is None:
      baseplates = self.baseplates
    for a, b in itertools.pairwise(baseplates):
      for (x1, y1), (x2, y2) in itertools.pairwise(plot_line(a.center, b.center)):
        yield x2, y2
        if x1 != x2 and y1 != y2:
          yield x1, y2

  def walk_pearl(self, grains: Iterable[Tuple[int, int]], max_layers=10):
    last_layer = list(grains)
    yield from (((x, y), 0) for (x, y) in last_layer)
    visited = {(x, y): (0, i) for i, (x, y) in enumerate(last_layer)}
    for layer_num in range(1, max_layers):
      this_layer = []
      # Starting at each point in the last layer,
      for x1, y1 in last_layer:
        done = False
        # Put the cursor at the point north of it facing east.
        cx, cy, cvx, cvy = x1, y1 - 1, 1, 0
        # Skip if this was already visited.
        if (cx, cy) in visited:
          done = True
        # For each point the cursor visits,
        while not done:
          # Yield the cursor point.
          visited[cx, cy] = (layer_num, len(this_layer))
          this_layer.append((cx, cy))
          yield (cx, cy), layer_num
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
            elif self.rng.random() < 0.8:
              # Move to it
              cx, cy, cvx, cvy = nx, ny, vx, vy
              break
          # If no possible movement was acceptable,
          else:
            # Finish exploring this point.
            done = True
      last_layer = this_layer




