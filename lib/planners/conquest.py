from collections.abc import Callable
import typing
from typing import Dict, Iterable, List, Optional, Set, Tuple, TYPE_CHECKING

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
    self._planners: List[Planner] = list(planners)

    self.spawn: Optional[SomaticPlanner] = None
    self.completed = 0
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
  def remaining(self) -> int:
    return self.total - self.completed

  @property
  def total(self) -> int:
    return len(self._planners)

  def intersecting(self, planner: Planner) -> Iterable[Planner]:
    indexes = set()
    for bp in planner.baseplates:
      indexes.update(self._bp_index[bp.id])
    for index in sorted(indexes):
      p = self._planners[index]
      if p != planner:
        yield p

  def flood(self):
    planners = typing.cast(List[StemPlanner], self._planners)

    rng = self.rng['flood']
    def coverage(min, max):
      return math.floor(
          rng.beta(a = 1.4, b = 1.4, min = min, max = max) * len(self._planners))
    water_count = coverage(*self.context.water_coverage)
    lava_count = coverage(*self.context.lava_coverage)
    dry: List[StemPlanner] = list(planners)
    
    # Flood fill with fluid via depth-first search
    def fill(count, fluid_type, spread):
      stack: List[StemPlanner] = []
      # The number of planners with this fluid is known
      for _ in range(count):
        # Pop 1 planner from the stack or choose a random one
        planner = stack.pop() if stack else rng.uniform_choice(
            p for p in dry if p.kind == StemPlanner.CAVE)
        # Fill the planner
        planner.fluid_type = fluid_type
        # Remove it from the list of dry
        dry.remove(planner)
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
    erodable = list(p for p in planners if p.fluid_type == Tile.LAVA)
    while erodable:
      planner = erodable.pop(rng.uniform_choice(range(len(erodable))))
      erode_chance = (
          self.context.cave_erode_chance if planner.kind == StemPlanner.CAVE
          else self.context.hall_erode_chance)
      if rng.chance(erode_chance):
        planner.has_erosion = True
        for p in self.intersecting(planner):
          p = typing.cast(StemPlanner, p)
          if (p not in erodable
              and not p.has_erosion
              and p.fluid_type != Tile.WATER
              and p.kind != planner.kind):
            erodable.append(p)
  
  def conquest(self):
    # Choose a cave to be the origin.
    spawn, spawn_fn = self._pick_spawn(typing.cast(Iterable[StemPlanner], self._planners))
    queue: List[StemPlanner] = [spawn]
    queue[0].hops_to_spawn = 0

    # Perform a breadth-first search on remaining planners to put them in the queue
    for i in range(self.total):
      stem = queue[i]
      for p in self.intersecting(stem):
        p = typing.cast(StemPlanner, p)
        if (p.kind != stem.kind  # Alternate between caves and halls
            and p not in queue):
          p.hops_to_spawn = stem.hops_to_spawn + 1
          queue.append(p)

    # Differentiate all items in queue
    for i, stem in enumerate(queue):
      def curved(curve: Curve) -> float:
        return (curve.base
            + curve.hops * stem.hops_to_spawn / queue[-1].hops_to_spawn
            + curve.completion * i / self.total)
      stem.crystal_richness   = curved(self.context.crystal_richness)
      stem.ore_richness       = curved(self.context.ore_richness)
      stem.monster_spawn_rate = curved(self.context.monster_spawn_rate)
      stem.monster_wave_size  = curved(self.context.monster_wave_size)
      if i == 0:
        planner = self.spawn = spawn_fn()
      else:
        planner = self._differentiate(stem)
      self._planners[planner.id] = planner
      self.expected_crystals += planner.expected_crystals
      yield planner
      self.completed = i + 1

  def _pick_spawn(self, planners: Iterable[StemPlanner]
      ) -> Tuple[StemPlanner, Callable[[], SomaticPlanner]]:
    def bids():
      for planner in planners:
        if planner._kind == StemPlanner.CAVE:
          for bidder in SPAWN_BIDDERS:
            for weight, fn in bidder(planner, self):
              yield weight, (planner, fn)
    return self.rng['differentiate'].weighted_choice(bids())

  def _differentiate(self, planner: StemPlanner) -> SomaticPlanner:
    bidders = None
    if planner._kind == StemPlanner.CAVE:
      bidders = CAVE_BIDDERS
    else:
      bidders = HALL_BIDDERS
    def bids():
      for bidder in bidders:
        yield from bidder(planner, self)
    return self.rng['differentiate'].weighted_choice(bids())()