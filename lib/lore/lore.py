from typing import Iterable, Optional, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from lib import Cavern

import collections
import math

from . import conclusions, openings, orders, premises

from lib.planners.caves import LostMinersCavePlanner, TreasureCavePlanner
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
    opening = self._opening(rng)
    premise = self._premise(rng)
    orders = self._orders(rng)
    return f'{opening}\n{premise}\n{orders}'
  
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

  # Opening lines.
    
  def _opening(self, rng) -> str:
    lava = 0
    water = 0
    total = 0
    for p in self.cavern.conquest.planners:
      if p.fluid_type == Tile.LAVA:
        lava += 1
      elif p.fluid_type == Tile.WATER:
        water += 1
      total += 1
    if lava / total > 0.4:
      return rng.uniform_choice(openings.LAVA_FLOODED)
    elif water / total > 0.4:
      return rng.uniform_choice(openings.WATER_FLOODED)
    else:
      return rng.uniform_choice(openings.NORMAL)

  # Premise - used in briefings, for flavor.
    
  def _premise(self, rng) -> str:
    positive = []
    negative = []

    positive.extend(self._premise_treasure(rng))
    negative.extend(self._premise_lost_miners(rng))

    if _spawn_has_erosion(self.cavern):
      negative.append(rng.uniform_choice(premises.SPAWN_HAS_EROSION))

    if positive and negative:
      bridge = rng.uniform_choice(premises.POSITIVE_NEGATIVE_BRIDGE)
      negative = _join_human(negative)
      if bridge[-1] in '.!?':
        negative = _capitalize_first(negative)
      return (
          f'{_capitalize_first(_join_human(positive))}. '
          f'{bridge} {negative}.')
    return _capitalize_first(
        _join_human(positive or negative)
        or rng.uniform_choice(premises.GENERIC)) + '.'

  def _premise_treasure(self, rng) -> Iterable[str]:
    planners = tuple(
        p for p in self.cavern.conquest.planners
        if isinstance(p, TreasureCavePlanner))
    if len(planners) == 1:
      yield rng.uniform_choice(premises.ONE_TREASURE_CAVE)
    elif planners:
      yield rng.uniform_choice(premises.TREASURE_CAVES)

  def _premise_lost_miners(self, rng) -> Iterable[str]:
    planners = tuple(
        p for p in self.cavern.conquest.planners
        if isinstance(p, LostMinersCavePlanner))
    if len(planners) == 1:
      lost_miners = sum(
          1 for o in self.cavern.diorama.objectives
          if isinstance(o, FindMinerObjective))
      if lost_miners == 1:
        yield rng.uniform_choice(premises.LOST_MINER)
      else:
        yield rng.uniform_choice(premises.LOST_MINERS_TOGETHER)
    elif planners:
      yield rng.uniform_choice(premises.LOST_MINERS_APART)


  # Orders - objectives phrased in briefings.

  def _resource_objective(self) -> Optional[ResourceObjective]:
    for o in self.cavern.diorama.objectives:
      if isinstance(o, ResourceObjective):
        return o
    return None
  
  def _non_resource_orders(self, rng) -> Iterable[str]:
    if _spawn_has_erosion(self.cavern):
      yield rng.uniform_choice(orders.SPAWN_HAS_EROSION)
    else:
      yield rng.uniform_choice(orders.GENERIC)
    lost_miners = sum(
        1 for o in self.cavern.diorama.objectives
        if isinstance(o, FindMinerObjective))
    if lost_miners > 0:
      if lost_miners > 1:
        miners = f'{_spell_number(lost_miners)} lost Rock Raiders'
      else:
        miners = 'lost Rock Raider'
      yield rng.uniform_choice(orders.FIND_LOST_MINERS) % miners

  def _resource_orders(self) -> Iterable[str]:
    o = self._resource_objective()
    if o:
      if o.crystals:
        yield f'{_spell_number(o.crystals)} Energy Crystals'
      if o.ore:
        yield f'{_spell_number(o.ore)} Ore'
      if o.studs:
        yield f'{_spell_number(o.studs)} Building Studs'

  def _orders(self, rng) -> str:
    nro = tuple(self._non_resource_orders(rng))
    ro = tuple(self._resource_orders())
    if not ro:
      return f'{_capitalize_first(_join_human(nro))}.'
    if len(ro) == 1:
      return f'{_capitalize_first(_join_human(nro + (f"collect {ro[0]}",)))}.'
    return (
        f'{_capitalize_first(_join_human(nro))}, '
        f'then collect {_join_human(ro)}.')

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
def _spawn_has_erosion(cavern: 'Cavern'):
  spawn = cavern.conquest.spawn
  return (
      spawn.has_erosion
      or any(p.has_erosion
             for p in cavern.conquest.intersecting(spawn)))