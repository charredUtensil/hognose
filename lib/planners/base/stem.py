from typing import Iterable, List, Literal, Optional, Tuple

import itertools

from lib.outlines import Baseplate, Path
from lib.planners.base.planner import Planner
from lib.plastic import Tile


class StemPlanner(Planner): # pylint:disable=too-many-instance-attributes
  HALL = 0
  CAVE = 1

  def __init__(self, id, context, baseplates, kind):
    super().__init__(id, context)
    self._baseplates = baseplates
    self._kind: Literal[
      StemPlanner.HALL,
      StemPlanner.CAVE] = kind
    self.hops_to_spawn: Optional[int] = None
    self.fluid_type: Optional[Literal[
      Tile.WATER,
      Tile.LAVA]] = None
    self.has_erosion = False
    self.crystal_richness = 0
    self.ore_richness = 0
    self.monster_spawn_rate = 0
    self.monster_wave_size = 0

  @property
  def baseplates(self) -> Tuple[Baseplate]:
    return self._baseplates

  @property
  def kind(self):
    return self._kind

  def rough(self, tiles):
    pass

  @property
  def pearl_radius(self):
    fn = max if self.kind == StemPlanner.CAVE else min
    return fn(bp.pearl_radius for bp in self.baseplates)

  @classmethod
  def from_outlines(
      cls,
      context,
      paths: List[Path],
      baseplates: List[Baseplate]) -> Iterable['StemPlanner']:
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


def average(a):
  t = 0
  c = 0
  for n in a:
    t += n
    c += 1
  return t // c
