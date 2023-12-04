import typing
from typing import Dict, Iterable, List, Optional, Set, TYPE_CHECKING

import collections
import math

from lib.base import Curve, ProceduralThing
from lib.planners.base import Planner, SomaticPlanner, StemPlanner
from lib.planners.caves import CAVE_BIDDERS, SPAWN_BIDDERS
from lib.planners.halls import HALL_BIDDERS
from lib.plastic import Tile

class Conquest(ProceduralThing):

  def __init__(self, context, planners: Iterable[StemPlanner]):
    super().__init__(-1, context)
    self._planners = list(planners)

    self.spawn_planner: Optional[SomaticPlanner] = None
    self.expected_crystals = 0

    self._bp_index: Dict[int, Set[int]] = {}
    for i, planner in enumerate(self._planners):
      for bp in planner.baseplates:
        id = bp.id
        if id not in self._bp_index:
          self._bp_index[id] = set()
        self._bp_index[id].add(i)

  @property
  def planners(self) -> Iterable[Planner]:
    return self._planners

  @property
  def somatic_planners(self) -> Iterable[SomaticPlanner]:
    return (p for p in self._planners if isinstance(p, SomaticPlanner))

  @property
  def completed(self) -> int:
    return sum(1 for p in self._planners if isinstance(p, SomaticPlanner))

  @property
  def remaining(self) -> int:
    return sum(1 for p in self._planners if isinstance(p, StemPlanner))

  @property
  def total(self) -> int:
    return sum(1 for p in self._planners)

  def intersecting(self, planner: Planner) -> Iterable[Planner]:
    indexes = set()
    for bp in planner.baseplates:
      indexes.update(self._bp_index[bp.id])
    for index in sorted(indexes):
      p = self._planners[index]
      if p != planner:
        yield p

  def flood(self):
    planners = typing.cast(StemPlanner, self._planners)

    rng = self.rng['flood']
    def coverage(min, max):
      return math.floor(
          rng.beta(a = 1.4, b = 1.4, min = min, max = max) * len(self._planners))
    water_count = coverage(*self.context.water_coverage)
    lava_count = coverage(*self.context.lava_coverage)
    queue: List[StemPlanner] = list(planners)
    
    # Flood fill with fluid via depth-first search
    def fill(count, fluid_type, spread):
      stack: List[StemPlanner] = []
      # The number of planners with this fluid is known
      for _ in range(count):
        # Pop 1 planner from the stack or choose a random one
        planner = stack.pop() if stack else rng.uniform_choice(
            p for p in queue if p.kind == StemPlanner.CAVE)
        # Fill the planner
        planner.fluid_type = fluid_type
        # Remove it from the queue of floodable planners
        queue.remove(planner)
        for p in self.intersecting(planner):
          p = typing.cast(StemPlanner, p)
          # Push intersecting planners onto the stack if:
          # - It is not already in the stack
          # - It does not already have a fluid
          # - It is not of the same kind (i.e. don't spread from hall to hall,
          #   skipping over a cave between them.)
          # - The RNG wills it.
          if (p not in stack
              and p.fluid_type is None
              and p.kind != planner.kind
              and rng.chance(spread)):
            stack.append(p)

    fill(water_count, Tile.WATER, self.context.water_spread)
    fill(lava_count, Tile.LAVA, self.context.lava_spread)

    # Flood fill with erosion (slightly different algorithm)
    queue = list(p for p in planners if p.fluid_type == Tile.LAVA)
    while queue:
      planner = queue.pop(rng.uniform_choice(range(len(queue))))
      erode_chance = (
          self.context.cave_erode_chance if planner.kind == StemPlanner.CAVE
          else self.context.hall_erode_chance)
      if rng.chance(erode_chance):
        planner.has_erosion = True
        for p in self.intersecting(planner):
          p = typing.cast(StemPlanner, p)
          if (p not in queue
              and not p.has_erosion
              and p.fluid_type != Tile.WATER
              and p.kind != planner.kind):
            queue.append(p)

  def _curved(self, curve: Curve, planner: StemPlanner) -> float:
    total = self.total
    return (curve.base
        + curve.distance * planner.hops_to_spawn / total
        + curve.completion * self.completed / total)
  
  def conquest(self):
    # Choose a cave to be the origin.
    # The one with the lowest ID might as well be random.
    self.spawn_planner = next(
        p for p in typing.cast(Iterable[StemPlanner], self.planners)
        if p.kind == StemPlanner.CAVE)
    queue: List[StemPlanner] = [self.spawn_planner]

    queue[0].hops_to_spawn = 0

    # Perform a breadth-first search on remaining planners
    while queue:
      stem = queue.pop(0)
      stem.crystal_richness = self._curved(self.context.crystal_richness, stem)
      stem.monster_spawn_rate = self._curved(self.context.monster_spawn_rate, stem)
      planner = self._differentiate(stem)
      self._planners[planner.id] = planner
      self.expected_crystals += planner.expected_crystals
      for p in self.intersecting(planner):
        if (isinstance(p, StemPlanner)
            and p.kind != stem.kind  # Alternate between caves and halls
            and p not in queue):
          p.hops_to_spawn = stem.hops_to_spawn + 1
          queue.append(p)
      yield planner

  def _differentiate(self, planner: StemPlanner) -> SomaticPlanner:
    bidders = None
    if all(isinstance(p, StemPlanner) for p in self.intersecting(planner)):
      bidders = SPAWN_BIDDERS
    elif planner._kind == StemPlanner.CAVE:
      bidders = CAVE_BIDDERS
    else:
      bidders = HALL_BIDDERS
    def bids():
      for bidder in bidders:
        yield from bidder(planner, self)
    return self.rng['conquest.differentiate'].weighted_choice(bids())()