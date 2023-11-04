from typing import Iterable, List, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
  from .conquest import Conquest

import itertools
import math

from lib.outlines import Baseplate, Path
from lib.planners.base import Planner, SomaticPlanner
from lib.planners.caves import CAVES, SPAWNS
from lib.planners.halls import HALLS
from lib.plastic import Tile

class StemPlanner(Planner):
  HALL = 0
  CAVE = 1

  def __init__(self, id, context, baseplates, kind):
    super().__init__(id, context, baseplates)
    self._kind: Literal[
      StemPlanner.HALL,
      StemPlanner.CAVE] = kind
    self.fluid_type: Optional[Literal[
      Tile.WATER,
      Tile.LAVA]] = None
    self.hops_to_spawn: Optional[int] = None

  @property
  def kind(self):
    return self._kind

  def suggested_crystal_count(self, conquest):
    area = sum(bp.area() for bp in self.baseplates)
    cf = math.sqrt(area) * (
      self.context.base_richness
      + self.context.hop_richness * self.hops_to_spawn / conquest.total
    )
    return (
      math.floor(max(0, self.rng.normal(1, 0.3)) * cf)
    )

  def differentiate(self, conquest: 'Conquest') -> SomaticPlanner:
    bidders = None
    if all(isinstance(p, StemPlanner) for p in conquest.intersecting(self)):
      bidders = SPAWNS
    elif self._kind == StemPlanner.CAVE:
      bidders = CAVES
    else:
      bidders = HALLS
    def bids():
      for klass in bidders:
        yield from klass.bids(self, conquest)
    return self.rng.bid(bids())()

  def rough(self, tiles):
    pass

  @classmethod
  def from_outlines(
      cls, context, paths: List[Path], baseplates: List[Baseplate]) -> Iterable['StemPlanner']:
    id_counter = itertools.count()
    big_cave_plates = set()
    big_cave_paths = []

    for kind in Path.SPANNING, Path.AUXILIARY:
      for path in paths:
        if path.kind == kind:
          if (len(path.baseplates) == 2
              and not big_cave_plates.intersection(path.baseplates)
              and path.origin.is_mergeable(path.destination)):
            big_cave_plates.update(path.baseplates)
            big_cave_paths.append(path)
          else:            
            yield StemPlanner(
                next(id_counter),
                context,
                path.baseplates,
                StemPlanner.HALL)
    for bp in baseplates:
      if bp.kind == Baseplate.SPECIAL and bp not in big_cave_plates:
        yield StemPlanner(
            next(id_counter), context, (bp,), StemPlanner.CAVE)
    for path in big_cave_paths:
      yield StemPlanner(
          next(id_counter), context, path.baseplates, StemPlanner.CAVE)