from typing import Iterable, Optional, Tuple

import enum
import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Creature, Diorama, Tile

class ScriptInfo(object):

  def __init__(
      self,
      discovery_tile: Optional[Tuple[int, int]],
      trigger_tiles: Iterable[Tuple[int, int]],
      secondary_trigger_tiles: Iterable[Tuple[int, int]],
      emerges: Iterable[Tuple[int, int, int]]):
    self.discovery_tile = discovery_tile
    self.trigger_tiles = tuple(trigger_tiles)
    self.secondary_trigger_tiles = tuple(secondary_trigger_tiles)
    self.emerges = tuple(emerges)

STATE_INACTIVE      = 0
STATE_RETRIGGERABLE = 1
STATE_COOLDOWN      = 2
STATE_READY         = 3

class RetriggerMode(enum.Enum):
  
  def __init__(self, after_trigger_state):
    self.after_trigger_state = after_trigger_state

  NEVER = (STATE_INACTIVE,)
  HOARD = (STATE_RETRIGGERABLE,)
  AUTOMATIC = (STATE_COOLDOWN,)

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
      retrigger_mode: RetriggerMode = RetriggerMode.AUTOMATIC):
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
    self.retrigger_mode = retrigger_mode
    self.script_info: Optional[ScriptInfo] = None

  def __str__(self):
    return (
        f'{self.wave_size:d}x{str(self.creature_type).split(".")[-1]}'
        f'/{(self.min_cooldown + self.max_cooldown)/2:.0f}s')

  def place_script(self, diorama: Diorama):
    self.script_info = ScriptInfo(
        self._discovery_tile(diorama),
        self._trigger_tiles(diorama),
        self._secondary_trigger_tiles(diorama),
        self._emerges(),
    )
    diorama.script.extend(self._gen_script(diorama))

  def _discovery_tile(self, diorama: Diorama) -> Optional[Tuple[int, int]]:
    for info in self.planner.pearl:
      if (not diorama.tiles[info.pos].is_wall
          and not info.pos in diorama.discovered):
        return info.pos
    return None

  def _trigger_tiles(self, diorama: Diorama) -> Iterable[Tuple[int, int]]:
    for info in self.planner.walk_pearl(
        (info.pos for info in self.planner.pearl),
        max_layers=2,
        baroqueness=0,
        include_nucleus=False):
      x, y = info.pos
      if diorama.tiles.get((x, y), Tile.SOLID_ROCK) != Tile.SOLID_ROCK:
        yield x, y

  def _secondary_trigger_tiles(self, diorama: Diorama) -> Iterable[Tuple[int, int]]:
    if self.retrigger_mode == RetriggerMode.HOARD:
      for info in self.planner.pearl:
        if (diorama.crystals.get(info.pos, 0) > 0
            and not diorama.tiles[info.pos].is_wall):
          yield info.pos

  def _emerges(self) -> Iterable[Tuple[int, int, int]]:
    for bp in self.planner.baseplates[:self.wave_size]:
      x, y = bp.center
      radius = min(bp.width, bp.height) // 2
      yield (math.floor(x), math.floor(y), radius)

  def _gen_script(self, diorama: Diorama) -> Iterable[str]:
    yield f'# {type(self).__name__} for planner #{self.planner.id}'
    prefix = f'p{self.planner.id}ms_'

    # Initialization
    # State of the spawner.
    yield f'int {prefix}state={STATE_INACTIVE}'
    # If there is a non-wall tile that starts undiscovered, generate an onActive
    # event chain that triggers when that tile changes (i.e. it becomes
    # discovered).
    if self.script_info.discovery_tile:
      x, y = self.script_info.discovery_tile
      yield f'if(change:y@{y:d},x@{x:d})[{prefix}onActive]'
    # Otherwise, just enable on init.
    else:
      yield f'if(time:0)[{prefix}onActive]'
    yield f'{prefix}onActive::;'
    # Wait for initial cooldown if there is one.
    if self.max_initial_cooldown > 0:
      yield (
          f'wait:random({self.min_initial_cooldown})'
          f'({self.max_initial_cooldown});')
    # Enable spawning
    yield f'{prefix}state={STATE_READY};'
    # Spawn immediately
    if self.spawn_immediately_when_ready:
      yield f'{prefix}spawn;'
    yield ''

    # Surround the cave with triggers that cause spawn.
    for x, y in self.script_info.trigger_tiles:
      yield f'when(enter:y@{y:d},x@{x:d})[{prefix}spawn]'
    
    # The actual spawn function
    yield f'{prefix}spawn::;'
    # Return if not ready
    yield f'(({prefix}state<{STATE_READY}))return;'
    yield f'{prefix}state={self.retrigger_mode.after_trigger_state};'
    # Emerge events
    for x, y, r in itertools.islice(itertools.cycle(
        self.script_info.emerges), self.wave_size):
      yield f'wait:random({self.min_delay:.2f})({self.max_delay:.2f});'
      yield f'emerge:y@{y:d},x@{x:d},A,{self.creature_type.value},{r:d};'
    # Wait for cooldown and re-enable
    if self.retrigger_mode != RetriggerMode.NEVER:
      yield f'wait:random({self.min_cooldown:.2f})({self.max_cooldown:.2f});'
      yield (
          f'(({prefix}state>={STATE_COOLDOWN}))'
          f'[{prefix}state={STATE_READY}][{prefix}state={STATE_INACTIVE}];')
    yield ''

    # Allow retrigger if a monster meets the crystal hoard.
    if self.retrigger_mode == RetriggerMode.HOARD:
      for x, y in self.script_info.secondary_trigger_tiles:
        yield f'when(enter:y@{y},x@{x},{self.creature_type.value})[{prefix}retrigger]'
      yield f'{prefix}retrigger::;'
      yield f'(({prefix}state=={STATE_RETRIGGERABLE})){prefix}state={STATE_COOLDOWN};'
      yield ''

  @classmethod
  def normal(
      cls,
      planner: SomaticPlanner,
      creature_type: Creature.Type,
      spawn_rate: float,
      mean_wave_size: float):
    rng = planner.rng['monster_spawner']
    wave_size = rng.beta_int(a = 5, b = 2, min = 1, max = mean_wave_size * 1.25)

    # Spawn the wave over 2-15 seconds
    min_delay = 2 / wave_size
    max_delay = 15 / wave_size

    mean_cooldown = 60 * wave_size / spawn_rate
    # Choose random min cooldown below the mean
    min_cooldown = rng.beta(a = 5, b = 5, min = 60, max = mean_cooldown)
    # Choose max cooldown so their average is the mean
    max_cooldown = 2 * mean_cooldown - min_cooldown

    return cls(
        planner,
        creature_type,
        wave_size,
        min_delay,
        max_delay,
        min_cooldown,
        max_cooldown,
    )