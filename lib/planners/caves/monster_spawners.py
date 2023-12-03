from typing import Iterable, Optional, Tuple

import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Creature, Diorama, Tile

class ScriptInfo(object):

  def __init__(
      self,
      discovery_tile: Optional[Tuple[int, int]],
      enter_triggers: Iterable[Tuple[int, int]],
      emerges: Iterable[Tuple[int, int, int]]):
    self.discovery_tile = discovery_tile
    self.enter_triggers = tuple(enter_triggers)
    self.emerges = tuple(emerges)

class MonsterSpawner(object):

  def __init__(
      self,
      planner: SomaticPlanner,
      creature_type: Creature.Type,
      wave_size: int = 3,
      min_delay: float = 1.9,
      max_delay: float = 5,
      min_cooldown: float = 60,
      max_cooldown: float = 300,
      min_initial_cooldown: float = 0,
      max_initial_cooldown: float = 0,
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
    self.script_info: Optional[ScriptInfo] = None

  def place_script(self, diorama: Diorama):
    self.script_info = ScriptInfo(
        self._discovery_tile(diorama),
        self._enter_triggers(diorama),
        self._emerges(),
    )
    diorama.script.extend(self._gen_script(diorama))

  def _discovery_tile(self, diorama: Diorama) -> Optional[Tuple[int, int]]:
    for info in self.planner.pearl:
      if (not diorama.tiles[info.pos].is_wall
          and not info.pos in diorama.discovered):
        return info.pos
    return None

  def _enter_triggers(self, diorama: Diorama) -> Iterable[Tuple[int, int]]:
    for info in self.planner.walk_pearl(
        (info.pos for info in self.planner.pearl),
        max_layers=2,
        baroqueness=0,
        include_nucleus=False):
      x, y = info.pos
      if diorama.tiles.get((x, y), Tile.SOLID_ROCK) != Tile.SOLID_ROCK:
        yield x, y

  def _emerges(self) -> Iterable[Tuple[int, int, int]]:
    for bp in self.planner.baseplates[:self.wave_size]:
      x, y = bp.center
      radius = min(bp.width, bp.height) // 2
      yield (math.floor(x), math.floor(y), radius)

  def _gen_script(self, diorama: Diorama) -> Iterable[str]:
    yield f'# {type(self).__name__} for planner #{self.planner.id}'
    prefix = f'p{self.planner.id}_monsterSpawner_'

    # Initialization
    yield f'bool {prefix}canSpawn'
    # If there is a non-wall tile that starts undiscovered, generate an onOpen
    # event chain that triggers when that tile changes (i.e. it becomes
    # discovered).
    if self.script_info.discovery_tile:
      x, y = self.script_info.discovery_tile
      yield f'if(change:x@{x:d},y@{y:d})[{prefix}onOpen]'
    # Otherwise, just enable on init.
    else:
      yield f'if(time:0)[{prefix}onOpen]'
    yield f'{prefix}onOpen::;'
    # Wait for initial cooldown if there is one.
    if self.max_initial_cooldown > 0:
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
    for x, y in self.script_info.enter_triggers:
      yield f'when(enter:y@{y:d},x@{x:d})[{prefix}spawn]'
    
    # The actual spawn function
    yield f'{prefix}spawn::;'
    # Return if not cooldown
    yield f'(({prefix}canSpawn==0))return;'
    yield f'{prefix}canSpawn=false;'
    # Emerge events
    for x, y, r in itertools.islice(itertools.cycle(
        self.script_info.emerges), self.wave_size):
      yield f'wait:random({self.min_delay:.2f})({self.max_delay:.2f});'
      yield f'emerge:y@{y:d},x@{x:d},A,{self.creature_type.value},{r:d};'
    # Wait for cooldown and re-enable
    if self.repeat:
      yield f'wait:random({self.min_cooldown:.2f})({self.max_cooldown:.2f});'
      yield f'{prefix}canSpawn=true;'
    yield ''

def generate_normal(
    planner: SomaticPlanner,
    creature_type: Creature.Type,
    spawn_rate: float):
  rng = planner.rng['monster_spawner']
  wave_size = math.floor(rng.beta(min=1, max=8, a=2.5, b=5))
  min_delay = 2 / wave_size
  max_delay = 15 / wave_size
  mean_cooldown = 60 * wave_size / spawn_rate
  min_cooldown = rng.beta(min=60, max=mean_cooldown, a=5, b=5)
  max_cooldown = 2 * mean_cooldown - min_cooldown
  return MonsterSpawner(
      planner,
      creature_type,
      wave_size,
      min_delay,
      max_delay,
      min_cooldown,
      max_cooldown,
  )