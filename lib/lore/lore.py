from typing import Iterable, Optional, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from lib import Cavern

import collections
import math

from . import conclusions, openings
from .orders import ORDERS
from .premises import PREMISES

from lib.base import Biome
from lib.planners.caves import EstablishedHQCavePlanner, LostMinersCavePlanner, TreasureCavePlanner
from lib.plastic import FindMinerObjective, ResourceObjective, Tile

class Lore(object):
  def __init__(self, cavern: 'Cavern'):
    self.cavern = cavern

  def level_name(self) -> str:
    #rng = self.cavern.context.rng['lore', 0]
    seed = f'{self.cavern.context.seed:08X}'
    return (
      'HN-'
      f'{self.cavern.context.biome.value[-1].upper()}'
      f'{seed[:3]}-{seed[3:]}')

  def briefing(self) -> str:
    rng = self.cavern.context.rng['lore', 1]
    flooded_kind = _flooded_kind(self.cavern)
    lost_miners = sum(
        1 for o in self.cavern.diorama.objectives
        if isinstance(o, FindMinerObjective))
    lost_miner_caves = sum(
        1 for p in self.cavern.conquest.planners
        if isinstance(p, LostMinersCavePlanner))
    monster_type = {
        Biome.ROCK: 'rock',
        Biome.ICE: 'ice',
        Biome.LAVA: 'lava',
    }[self.cavern.context.biome]
    treasure_count = sum(
        1 for p in self.cavern.conquest.planners
        if isinstance(p, TreasureCavePlanner))
    resources = _join_human(tuple(self._resources_for_briefing()))
    spawn = self.cavern.conquest.spawn
    spawn_is_ruins = (
        isinstance(spawn, EstablishedHQCavePlanner) and spawn.is_ruin)
    find_hq = not spawn_is_ruins and any(
        isinstance(p, EstablishedHQCavePlanner) for p in self.cavern.conquest.planners
    )

    premise = PREMISES.generate(rng, {
        'has_monsters': self.cavern.context.has_monsters,
        #'find_hq': find_hq,
        'flooded_lava': flooded_kind == Tile.LAVA,
        'flooded_water': flooded_kind == Tile.WATER,
        'lost_miners_one': lost_miners == 1,
        'lost_miners_together': lost_miners > 1 and lost_miner_caves == 1,
        'lost_miners_many': lost_miner_caves > 1,
        'spawn_has_erosion': _spawn_has_erosion(self.cavern),
        'spawn_is_ruins': spawn_is_ruins,
        'treasure_one': treasure_count == 1,
        'treasure_many': treasure_count > 1,
    })
    orders = ORDERS.generate(rng, {
        'collect_resources': bool(resources),
        'find_hq': find_hq,
        'has_monsters': self.cavern.context.has_monsters,
        'lost_miners_one': lost_miners == 1,
        'lost_miners_many': lost_miners > 1,
        'spawn_has_erosion': _spawn_has_erosion(self.cavern),
        'spawn_is_ruins': spawn_is_ruins,
    })
    return f'{premise}\n{orders}' % {
        'resources': resources
    }
  
  def success(self) -> str:
    rng = self.cavern.context.rng['lore', 2]
    opening = rng.uniform_choice(openings.SUCCESS)
    conclusion = self._objectives_achieved(rng)
    congratulation = rng.uniform_choice(conclusions.CONGRATULATION)
    return f'{opening} {conclusion} {congratulation}'
  
  def failure(self) -> str:
    rng = self.cavern.context.rng['lore', 3]
    opening = rng.uniform_choice(openings.FAILURE)
    conclusion = self._objectives_failed(rng)
    condolence = rng.uniform_choice(conclusions.CONDOLENCE)
    return f'{opening} {conclusion} {condolence}'

  def _resource_objective(self) -> Optional[ResourceObjective]:
    for o in self.cavern.diorama.objectives:
      if isinstance(o, ResourceObjective):
        return o
    return None

  def _resources_for_briefing(self) -> Iterable[str]:
    o = self._resource_objective()
    if o:
      if o.crystals:
        yield f'{_spell_number(o.crystals)} Energy Crystals'
      if o.ore:
        yield f'{_spell_number(o.ore)} Ore'
      if o.studs:
        yield f'{_spell_number(o.studs)} Building Studs'

  # Conclusions - success and failure messages based on objectives.

  def _objectives_conclusion(self, rng) -> str:
    result = []

    lost_miners = sum(
        1 for o in self.cavern.diorama.objectives
        if isinstance(o, FindMinerObjective))
    if lost_miners > 0:
      result.append(f'find the lost Rock Raider{"s" if lost_miners > 1 else ""}')
    
    ro = self._resource_objective()
    if ro:
      resources = tuple((s, qty) for s, qty in (
          (f'Energy Crystals', ro.crystals),
          (f'ore', ro.ore),
          (f'Building Studs', ro.studs)) if qty > 0)
      if len(resources) > 1:
        resource = 'the resources'
      else:
        resource = f'{_spell_number(resources[0][1])} {resources[0][0]}'
      result.append(rng.uniform_choice(conclusions.RESOURCES) % resource)

    return _join_human(result)

  def _objectives_achieved(self, rng) -> str:
    return (
        rng.uniform_choice(conclusions.ACHIEVED)
        % self._objectives_conclusion(rng))

  def _objectives_failed(self, rng) -> str:
    return (
        rng.uniform_choice(conclusions.FAILED)
        % self._objectives_conclusion(rng))


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
    
def _spawn_has_erosion(cavern: 'Cavern'):
  spawn = cavern.conquest.spawn
  return (
      spawn.has_erosion
      or any(p.has_erosion
             for p in cavern.conquest.intersecting(spawn)))