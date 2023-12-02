from typing import Iterable

import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Creature, Diorama, Tile

class MonsterSpawner(object):

  def __init__(
      self,
      planner: SomaticPlanner,
      creature_type: Creature.Type,
      wave_size: int = 3,
      min_delay: float = 1.9,
      max_delay: float = 5,
      min_cooldown: int = 60,
      max_cooldown: int = 300,
      min_initial_cooldown: int = 0,
      max_initial_cooldown: int = 0,
      spawn_immediately_when_ready = False,
      repeat: bool = True):
    self.planner = planner
    self.creature_type = creature_type
    self.wave_size = wave_size
    self.min_delay = min_delay
    self.max_delay = max_delay
    self.min_cooldown = min_cooldown
    self.max_cooldown = max_cooldown
    self.min_initial_cooldown = min_initial_cooldown
    self.max_initial_cooldown = max_initial_cooldown
    self.spawn_immediately_when_ready = spawn_immediately_when_ready
    self.repeat = repeat

  def place_script(self, diorama: Diorama):
    diorama.script.extend(self._gen_script(diorama))

  def _gen_script(self, diorama: Diorama) -> Iterable[str]:
    yield f'# {type(self).__name__} for planner #{self.planner.id}'
    prefix = f'p{self.planner.id}_monsterSpawner_'

    # Initialization
    yield f'bool {prefix}canSpawn'
    # If there is a non-wall tile that starts undiscovered, generate an onOpen
    # event chain that triggers when that tile changes (i.e. it becomes
    # discovered).
    for info in self.planner.pearl:
      if (not diorama.tiles[info.pos].is_wall
          and not info.pos in diorama.discovered):
        x, y = info.pos
        yield f'if(change:x@{x:d},y@{y:d})[{prefix}onOpen]'
        break
    # Otherwise, just enable on init.
    else:
      yield f'if(time:0)[{prefix}onOpen]'
    yield f'{prefix}onOpen::;'
    # Wait for initial cooldown if there is one.
    if self.max_initial_cooldown:
      yield (
          f'wait:random({self.min_initial_cooldown})'
          f'({self.max_initial_cooldown});')
    # Enable spawning
    yield f'{prefix}canSpawn=true;'
    # Spawn immediately
    if self.spawn_immediately_when_ready:
      yield f'{prefix}spawn;'
    yield ''

    # Surround the cave with enter triggers.
    for info in self.planner.walk_pearl(
        (info.pos for info in self.planner.pearl),
        max_layers=2,
        baroqueness=0,
        include_nucleus=False):
      x, y = info.pos
      if diorama.tiles.get((x, y), Tile.SOLID_ROCK) != Tile.SOLID_ROCK:
        yield f'when(enter:y@{y:d},x@{x:d})[{prefix}spawn]'
    
    # The actual spawn function
    yield f'{prefix}spawn::;'
    # Return if not cooldown
    yield f'(({prefix}canSpawn==0))return;'
    yield f'{prefix}canSpawn=false;'
    # Emerge events
    for bp in itertools.islice(
        itertools.cycle(self.planner.baseplates), self.wave_size):
      x, y = bp.center
      x = math.floor(x)
      y = math.floor(y)
      radius = min(bp.width, bp.height) // 2
      yield f'wait:random({self.min_delay:.2f})({self.max_delay:.2f});'
      yield f'emerge:y@{y:d},x@{x:d},A,{self.creature_type.value},{radius:d};'
    # Wait for cooldown and re-enable
    if self.repeat:
      yield f'wait:random({self.min_cooldown:d})({self.max_cooldown:d});'
      yield f'{prefix}canSpawn=true;'
    yield ''