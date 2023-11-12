from typing import Dict, Iterable, List, Literal, Tuple

import math

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

  def weave(self):
    if self.rng['weave'].random() < self._context.weave_chance:
      self.kind = Path.AUXILIARY
    else:
      self.kind = Path.EXCLUDED

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

    def plates(path: 'Path') -> Iterable[Baseplate]:
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
              if last.kind == Baseplate.AMBIGUOUS:
                last.kind = Baseplate.HALL
              yield last
              break

    relevant_kinds = frozenset((Path.SPANNING, Path.AUXILIARY))
    for path in paths:
      if path.kind in relevant_kinds:
        path.baseplates = tuple(plates(path))
    
    for bp in baseplates:
      if bp.kind == Baseplate.AMBIGUOUS:
         bp.kind = Baseplate.EXCLUDED