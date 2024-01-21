from typing import Iterable, Optional, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from lib import Cavern

import collections
import functools
import math

from .conclusions import SUCCESS, FAILURE
from .events import FOUND_HOARD, FOUND_HQ
from .orders import ORDERS
from .premises import PREMISES

from lib.base import Biome
from lib.planners.caves import EstablishedHQCavePlanner, LostMinersCavePlanner, TreasureCavePlanner
from lib.plastic import FindMinerObjective, ResourceObjective, Tile

class Lore(object):
  def __init__(self, cavern: 'Cavern'):
    self.cavern = cavern

    resources = _resources(cavern)

    def states():
      flooded_kind = _flooded_kind(self.cavern)
      if flooded_kind == Tile.WATER:
        yield 'flooded_water'
      if flooded_kind == Tile.LAVA:
        yield 'flooded_lava'

      lost_miners_count = sum(
          1 for o in self.cavern.diorama.objectives
          if isinstance(o, FindMinerObjective))
      if lost_miners_count:
        lost_miner_caves_count = sum(
            1 for p in self.cavern.conquest.planners
            if isinstance(p, LostMinersCavePlanner))
        if lost_miners_count == 1:
          yield 'lost_miners_one'
        elif lost_miner_caves_count == 1:
          yield 'lost_miners_together'
        else:
          yield 'lost_miners_apart'
      
      if resources:
        yield 'collect_resources'

      if self.cavern.context.has_monsters:
        yield 'has_monsters'

      spawn = self.cavern.conquest.spawn
      if _spawn_has_erosion(self.cavern):
        yield 'spawn_has_erosion'
      if isinstance(spawn, EstablishedHQCavePlanner):
        if spawn.is_ruin:
          yield 'spawn_is_ruin'
        else:
          yield 'spawn_is_hq'
      elif any(
          isinstance(p, EstablishedHQCavePlanner)
          for p in self.cavern.conquest.planners):
        yield 'find_hq'

      treasure_count = sum(
          1 for p in self.cavern.conquest.planners
          if isinstance(p, TreasureCavePlanner))
      if treasure_count == 1:
        yield 'treasure_one'
      elif treasure_count > 1:
        yield 'treasure_many'

    self._states = frozenset(states())
    self._vars = {
      'monster_type': {
          Biome.ROCK: 'rock',
          Biome.ICE: 'ice',
          Biome.LAVA: 'lava',
      }[self.cavern.context.biome],
      'resources': resources}

  @functools.cached_property
  def level_name(self) -> str:
    seed = f'{self.cavern.context.seed:08X}'
    return (
      'HN-'
      f'{self.cavern.context.biome.value[-1].upper()}'
      f'{seed[:3]}-{seed[3:]}')

  @functools.cached_property
  def briefing(self) -> str:
    rng = self.cavern.context.rng['lore', -1]
    premise = PREMISES.generate(rng, self._states)
    orders = ORDERS.generate(rng, self._states)
    return f'{premise}\n{orders}' % self._vars
  
  @functools.cached_property
  def success(self) -> str:
    rng = self.cavern.context.rng['lore', -2]
    return SUCCESS.generate(
        rng, self._states | frozenset(('commend',))) % self._vars
  
  @functools.cached_property
  def failure(self) -> str:
    rng = self.cavern.context.rng['lore', -3]
    return FAILURE.generate(
        rng, self._states | frozenset(('console',))) % self._vars

  @functools.cached_property
  def event_found_hoard(self) -> str:
    rng = self.cavern.context.rng['lore', -4]
    return FOUND_HOARD.generate(rng, self._states) % self._vars

  @functools.cached_property
  def event_found_hq(self) -> str:
    rng = self.cavern.context.rng['lore', -5]
    return FOUND_HQ.generate(rng, self._states) % self._vars

# String manipulation methods
def _capitalize_first(s: str) -> str:
  return s[0].upper() + s[1:] if s else s

def _join_human(things: Sequence[str], conjunction: str = 'and') -> str:
  if len(things) == 0:
    return ''
  if len(things) == 1:
    return things[0]
  return f'{", ".join(things[:-1])} {conjunction} {things[-1]}'

def _spell_cardinal(
    origin: Tuple[float, float],
    destination: Tuple[float, float]):
  x1, y1 = origin
  x2, y2 = destination
  return (
    'east', 'north east', 'north', 'north west',
    'west', 'south west', 'south', 'south east', 'east'
  )[round(4 * (math.atan2(y2 - y1, x2 - x1) / math.pi + 1))]

def _spell_number(n: int) -> str:
  if n > 999:
    return str(n)
  r = []
  while n > 0:
    if n >= 100:
      r.append(f'{_spell_number(n // 100)} hundred')
      n = n % 100
    elif n >= 20:
      r.append((
          'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty',
          'ninety')[(n // 10) - 2])
      n = n % 10
    else:
      r.append((
          'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
          'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
          'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen')[n - 1])
      n = 0
  return ' '.join(r)

# Helper methods

def _flooded_kind(cavern: 'Cavern'):
  lava = 0
  water = 0
  total = 0
  for p in cavern.conquest.planners:
    if p.fluid_type == Tile.LAVA:
      lava += 1
    elif p.fluid_type == Tile.WATER:
      water += 1
    total += 1
  if lava / total > 0.4:
    return Tile.LAVA
  elif water / total > 0.4:
    return Tile.WATER
  else:
    return None

def _resources(cavern):
  def h():
    for o in cavern.diorama.objectives:
      if isinstance(o, ResourceObjective):
        if o.crystals:
          yield f'{_spell_number(o.crystals)} Energy Crystals'
        if o.ore:
          yield f'{_spell_number(o.ore)} Ore'
        if o.studs:
          yield f'{_spell_number(o.studs)} Building Studs'
        return
  return _join_human(tuple(h()))
    
def _spawn_has_erosion(cavern: 'Cavern'):
  spawn = cavern.conquest.spawn
  return (
      spawn.has_erosion
      or any(p.has_erosion
             for p in cavern.conquest.intersecting(spawn)))