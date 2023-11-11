from typing import Iterable, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
  from lib import Cavern

import collections

from . import conclusions, openings, orders, premises

from lib.plastic import FindMinerObjective, ResourceObjective, Tile

class Lore(object):
  def __init__(self, cavern: 'Cavern'):
    self.cavern = cavern

  def level_name(self) -> str:
    #rng = self.cavern.context.rng['lore', 0]
    return f'HN-{hex(self.cavern.context.seed)[2:]}'

  def briefing(self) -> str:
    rng = self.cavern.context.rng['lore', 1]
    opening = self._opening(rng)
    premise = self._premise(rng)
    orders = self._orders(rng)
    return f'{opening}\n{premise}\n{orders}'
  
  def success(self) -> str:
    rng = self.cavern.context.rng['lore', 2]
    opening = rng.choice(openings.SUCCESS)
    conclusion = self._objectives_achieved(rng)
    congratulation = rng.choice(conclusions.CONGRATULATION)
    return f'{opening} {conclusion} {congratulation}'
  
  def failure(self) -> str:
    rng = self.cavern.context.rng['lore', 3]
    opening = rng.choice(openings.FAILURE)
    conclusion = self._objectives_failed(rng)
    condolence = rng.choice(conclusions.CONDOLENCE)
    return f'{opening} {conclusion} {condolence}'

  # Opening lines.
    
  def _opening(self, rng) -> str:
    lava = 0
    water = 0
    total = 0
    for p in self.cavern.conquest.stem_planners:
      if p.fluid_type == Tile.LAVA:
        lava += 1
      elif p.fluid_type == Tile.WATER:
        water += 1
      total += 1
    if lava / total > 0.4:
      return rng.choice(openings.LAVA_FLOODED)
    elif water / total > 0.4:
      return rng.choice(openings.WATER_FLOODED)
    else:
      return rng.choice(openings.NORMAL)

  # Premise - used in briefings, for flavor.
    
  def _premise(self, rng) -> str:
    planner_kinds = collections.Counter()
    for p in self.cavern.conquest.somatic_planners:
      planner_kinds[type(p).__name__] += 1
   
    positive = []
    negative = []

    treasure = planner_kinds['TreasureCavePlanner']
    if treasure > 0:
      positive.append(rng.choice(
          premises.ONE_TREASURE_CAVE if treasure == 1
          else premises.TREASURE_CAVES))

    lost_miners = planner_kinds['LostMinersCavePlanner']
    if lost_miners > 0:
      negative.append(rng.choice(
          premises.LOST_MINERS_TOGETHER if lost_miners == 1
          else premises.LOST_MINERS_APART))

    if self.cavern.conquest.spawn_planner.has_erosion:
      negative.append(rng.choice(premises.SPAWN_HAS_EROSION))

    if positive and negative:
      bridge = rng.choice(premises.POSITIVE_NEGATIVE_BRIDGE)
      return (
          f'{_capitalize_first(_join_human(positive))}. '
          f'{bridge} {_join_human(negative)}.')
    return _capitalize_first(
        _join_human(positive or negative)
        or rng.choice(premises.GENERIC)) + '.'


  # Orders - objectives phrased in briefings.

  def _resource_objective(self) -> Optional[ResourceObjective]:
    for o in self.cavern.diorama.objectives:
      if isinstance(o, ResourceObjective):
        return o
    return None
  
  def _non_resource_orders(self, rng) -> Iterable[str]:
    if self.cavern.conquest.spawn_planner.has_erosion:
      yield rng.choice(orders.SPAWN_HAS_EROSION)
    else:
      yield rng.choice(orders.GENERIC)
    lost_miners = sum(
        1 for o in self.cavern.diorama.objectives
        if isinstance(o, FindMinerObjective))
    if lost_miners > 0:
      if lost_miners > 1:
        miners = f'{_spell_number(lost_miners)} lost miners'
      else:
        miners = 'lost miner'
      yield rng.choice(orders.FIND_LOST_MINERS) % miners

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
      result.append(f'find the lost miner{"s" if lost_miners > 1 else ""}')
    
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
      result.append(rng.choice(conclusions.RESOURCES) % resource)

    return _join_human(result)

  def _objectives_achieved(self, rng) -> str:
    return (
        rng.choice(conclusions.ACHIEVED)
        % self._objectives_conclusion(rng))

  def _objectives_failed(self, rng) -> str:
    return (
        rng.choice(conclusions.FAILED)
        % self._objectives_conclusion(rng))

def _capitalize_first(s: str) -> str:
  return s[0].upper() + s[1:] if s else s

def _join_human(things: Sequence[str], conjunction: str = 'and') -> str:
  if len(things) == 0:
    return ''
  if len(things) == 1:
    return things[0]
  return f'{", ".join(things[:-1])} {conjunction} {things[-1]}'

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