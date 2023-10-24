from typing import Dict, Optional, Tuple

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

  def walk_tube(self, baseplates=None, radius=4):
    if baseplates is None:
      baseplates = self.baseplates
    return tube_coords((bp.center for bp in baseplates), 4).items()

  def walk_blob(self, baseplates=None):
    if baseplates is None:
      baseplates = self.baseplates
    thickness = min(max(bp.width, bp.height) for bp in baseplates) / 2

    # Find tube coords
    tube = None
    if len(baseplates) > 1:
      tube = tube_coords((bp.center for bp in baseplates), thickness)
    else:
      radius = max(baseplates[0].width, baseplates[0].height) / 4
      x, y = baseplates[0].center
      ox, oy = self.rng.point_in_circle(radius)
      tube = tube_coords(((x + ox, y + oy), (x - ox, y - oy)), thickness)

    # Find radial coords
    radial = {}
    for bp in baseplates:
      cx, cy = bp.center
      w = bp.width
      h = bp.height
      for x in range(bp.left, bp.right):
        for y in range(bp.top, bp.bottom):
          dist = math.sqrt(((x - cx) / w) ** 2 + ((y - cy) / h) ** 2)
          if (x, y) not in radial or dist < radial[x, y]:
            radial[x, y] = dist

    # Meld them together
    result = {}
    coords = set(tube.keys())
    coords.update(radial.keys())
    for x, y in coords:
      u, v = tube.get((x, y), (1, 1))
      w = radial.get((x, y), 1)
      result[x, y] = min(max(u, w), 1) * 0.15 + min(u, w, 1) * 0.85
    return result.items()
    

def line_segment_coords(x, y, x1, y1, x2, y2):
  l2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
  t = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / l2
  t = max(0, min(1, t))
  return (
    math.sqrt(
      (x - (x1 + t * (x2 - x1))) ** 2 +
      (y - (y1 + t * (y2 - y1))) ** 2),
    t)

def tube_coords(points, max_radius):
  result = {}
  for i, ((x1, y1), (x2, y2)) in enumerate(itertools.pairwise(points)):
    # Compute a simple bounding box for tiles added by the segment
    left   = math.floor(min(x1, x2) - max_radius)
    top    = math.floor(min(y1, y2) - max_radius)
    right  = math.ceil( max(x1, x2) + max_radius)
    bottom = math.ceil( max(y1, y2) + max_radius)
    # Iterate over pixels in the bounding box and compute distance
    for x in range(left, right):
      for y in range(top, bottom):
        u, v = line_segment_coords(x, y, x1, y1, x2, y2)
        u /= max_radius
        if u <= 1:
          if (x, y) not in result or result[x, y][0] > u:
            result[x, y] = (u, (v + i))
  return result