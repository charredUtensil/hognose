from typing import Dict, Iterable, List, Literal, Set, Tuple

import math
import operator

from .baseplate import Baseplate
from lib.base import Context, ProceduralThing
from lib.utils.geometry import plot_line

class Path(ProceduralThing):
  AMBIGUOUS = 'ambiguous'
  EXCLUDED  = 'excluded'
  SPANNING  = 'spanning'
  AUXILIARY = 'auxiliary'

  def __init__(self, id: int, context: Context, baseplates: Iterable[Baseplate]):
    super().__init__(id, context)
    self.kind: Literal[
      Path.AMBIGUOUS,
      Path.EXCLUDED,
      Path.SPANNING,
      Path.AUXILIARY
      ] = Path.AMBIGUOUS
    self.baseplates = tuple(baseplates)

  @property
  def origin(self) -> Baseplate:
    return self.baseplates[0]

  @property
  def destination(self) -> Baseplate:
    return self.baseplates[-1]

  def __repr__(self):
    return 'Path {self.kind}: ' + '>'.join(str(b.id) for b in self.baseplates)

  def bat_distance(self) -> float:
    x1, y1 = self.origin.center
    x2, y2 = self.destination.center
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx*dx + dy*dy)

  @staticmethod
  def minimum_spanning_tree(paths):
    next_cluster = 0
    clusters = {}
    for path in sorted(paths, key=Path.bat_distance):
      origin = path.origin
      destination = path.destination
      if origin in clusters:
        if destination in clusters:
          origin_cluster = clusters[origin]
          destination_cluster = clusters[destination]
          if destination_cluster == origin_cluster:
            # This would create a cycle. Skip it.
            continue
          else:
            # This connects two existing clusters. Unite them.
            for k, v in tuple(clusters.items()):
              if v == destination_cluster:
                clusters[k] = origin_cluster
        else:
          # Destination is not yet clustered. Add it to the origin's cluster.
          clusters[destination] = clusters[origin]
      else:
        if destination in clusters:
          # Origin is not yet clustered. Add it to the destination's cluster.
          clusters[origin] = clusters[destination]
        else:
          # Neither lots are clustered. Create a new cluster.
          clusters[origin] = next_cluster
          clusters[destination] = next_cluster
          next_cluster += 1
      path.kind = Path.SPANNING

  @staticmethod
  def bore(paths: List['Path'], baseplates: List[Baseplate]):
    baseplate_index: Dict[Tuple[int, int], Baseplate] = {}
    for bp in baseplates:
      for x in range(bp.left, bp.right):
        for y in range(bp.top, bp.bottom):
          baseplate_index[x, y] = bp

    def gen_path_plates(path: 'Path') -> Iterable[Baseplate]:
      last = path.origin
      seen = set((last,))
      yield last
      while True:
        for x, y in plot_line(last.center, path.destination.center):
          bp = baseplate_index.get((x, y))
          if bp == path.destination:
            yield bp
            return
          if bp and bp not in seen:
            seen.add(bp)
            if bp.kind != Baseplate.SPECIAL:
              last = bp
              yield last
              break

    for path in paths:
      if path.kind == Path.EXCLUDED:
        continue
      path.baseplates = tuple(gen_path_plates(path))

  @staticmethod
  def weave(context, paths):
    # Compute the absolute angles of spanning paths at each baseplate.
    angles: Dict[int, Set[float]] = {}
    for p in paths:
      if p.kind == Path.SPANNING:
        _make_halls(p.baseplates)
        for a, b in (
            (p.baseplates[0], p.baseplates[1]),
            (p.baseplates[-1], p.baseplates[-2])):
          if a.id not in angles:
            angles[a.id] = set()
          ax, ay = a.center
          bx, by = b.center
          angles[a.id].add(math.atan2(by - ay, bx - ax))

    # Compute the minimum relative angle between each end of a non-spanning
    # path and a spanning path.
    def relative_angles(p):
      for a, b in (
          (p.baseplates[ 0], p.baseplates[ 1]),
          (p.baseplates[-1], p.baseplates[-2])):
        ax, ay = a.center
        bx, by = b.center
        theta = math.atan2(by - ay, bx - ax)
        def h():
          for span_theta in angles[a.id]:
            delta = abs(theta - span_theta)
            # Invert reflex angles
            if delta > math.pi:
              yield 2 * math.pi - delta
            else:
              yield delta
        yield min(h())
    
    # Exclude any path with a relative angle less than 45 degrees.
    for p in paths:
      if p.kind == Path.AMBIGUOUS:
        if min(relative_angles(p)) < math.pi / 4:
          p.kind = Path.EXCLUDED
    yield

    # Choose the n candidates that make the widest minimum angle.
    candidates = sorted((
        (sum(relative_angles(p)), p) for p in paths if p.kind == Path.AMBIGUOUS
    ), key=operator.itemgetter(0), reverse=True)
    aux_count = context.weave_ratio * len(candidates)
    for i, (_, p) in enumerate(candidates):
      if i <= aux_count:
        p.kind = Path.AUXILIARY
        _make_halls(p.baseplates)
      else:
        p.kind = Path.EXCLUDED
    yield

def _make_halls(baseplates):
  for bp in baseplates:
    if bp.kind == Baseplate.AMBIGUOUS:
      bp.kind = Baseplate.HALL