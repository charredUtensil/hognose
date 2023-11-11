from typing import Dict, List, Set, TYPE_CHECKING

import collections
import math

from .stem import StemPlanner
from lib.base import ProceduralThing
from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class Conquest(ProceduralThing):

  def __init__(self, context, stem_planners):
    super().__init__(-1, context)
    self._stem_planners = list(stem_planners)
    self._somatic_planners = [None] * len(self._stem_planners)

    self.spawn_planner: Optional[SomaticPlanner] = None
    self.expected_crystals = 0

    self._bp_index: Dict[int, Set[int]] = {}
    for i, planner in enumerate(self.stem_planners):
      for bp in planner.baseplates:
        id = bp.id
        if id not in self._bp_index:
          self._bp_index[id] = set()
        self._bp_index[id].add(i)

  @property
  def stem_planners(self):
    return self._stem_planners

  @property
  def somatic_planners(self):
    return self._somatic_planners

  @property
  def planners(self):
    for stem, somatic in zip(self._stem_planners, self._somatic_planners):
      yield somatic or stem

  @property
  def completed(self):
    return sum(1 for p in self._somatic_planners if p)

  @property
  def remaining(self):
    return sum(1 for p in self._somatic_planners if p is None)

  @property
  def total(self):
    return sum(1 for p in self._somatic_planners)

  def intersecting(self, planner):
    indexes = set()
    for bp in planner.baseplates:
      indexes.update(self._bp_index[bp.id])
    return tuple(
        (self._somatic_planners[index] or self._stem_planners[index])
        for index in sorted(indexes))

  def flood(self):
    queue: List[StemPlanner] = list(self.stem_planners)
    water_count = math.floor(
        self.context.water_level * len(self._stem_planners))
    lava_count = math.floor(
        self.context.lava_level * len(self._stem_planners))
    rng = self.rng['flood']
    
    def fill(count, fluid_type, spread):
      stack: List[StemPlanner] = []
      for _ in range(count):
        if not stack:
          stack.append(rng.choice(
            p for p in queue if p.kind == StemPlanner.CAVE))
        planner = stack.pop()
        planner.fluid_type = fluid_type
        queue.remove(planner)
        for p in self.intersecting(planner):
          if (p not in stack
              and p.fluid_type is None
              and p.kind != planner.kind
              and rng.random() < spread):
            stack.append(p)

    fill(water_count, Tile.WATER, self.context.water_spread)
    fill(lava_count, Tile.LAVA, self.context.lava_spread)

    queue = list(p for p in self.stem_planners if p.fluid_type == Tile.LAVA)
    while queue:
      planner = queue.pop(math.floor(rng.random() * len(queue)))
      erode_chance = (
          self.context.cave_erode_chance if planner.kind == StemPlanner.CAVE
          else self.context.hall_erode_chance)
      if rng.random() < erode_chance:
        planner.has_erosion = True
        for p in self.intersecting(planner):
          if (p not in queue
              and not p.has_erosion
              and p.fluid_type != Tile.WATER
              and p.kind != planner.kind):
            queue.append(p)

  
  def conquest(self):
    # Choose a cave to be the origin
    self.spawn_planner = next(
      p for p in self.stem_planners
      if p.kind == StemPlanner.CAVE)
    queue: List[StemPlanner] = [self.spawn_planner]

    queue[0].hops_to_spawn = 0

    # Perform a breadth-first search on remaining planners
    while queue:
      stem = queue.pop(0)
      planner = stem.differentiate(self)
      self._somatic_planners[planner.id] = planner
      self.expected_crystals += planner.expected_crystals
      for p in self.intersecting(planner):
        if (isinstance(p, StemPlanner)
            and p.kind != stem.kind  # Alternate between caves and halls
            and p not in queue):
          p.hops_to_spawn = stem.hops_to_spawn + 1
          queue.append(p)
      yield planner