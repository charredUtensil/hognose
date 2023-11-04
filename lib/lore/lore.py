from typing import Iterable, Optional, Sequence

import collections

from lib.plastic import ResourceObjective, Tile

class Lore(object):
  def __init__(self, cavern: 'Cavern'):
    self.cavern = cavern

  def briefing(self) -> str:
    rng = self.cavern.context.rng(-1)
    opening = rng.choice(self._briefing_openings())
    premise = ' '.join(self._premise())
    objective = self._briefing_objective()
    return '\n'.join((opening, premise, objective))
  
  def success(self) -> str:
    rng = self.cavern.context.rng(-2)
    opening = rng.choice(self._success_openings())
    return f'{opening}\nMission Complete!'
  
  def failure(self) -> str:
    rng = self.cavern.context.rng(-3)
    opening = rng.choice(self._failure_openings())
    return f'{opening}\nMission Failed!'

  # Opening lines.
    
  def _briefing_openings(self) -> Iterable[str]:
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
      yield 'I hope you\'re not afraid of a little heat!'
    elif water / total > 0.4:
      yield 'Are you ready to set sail?'
      yield 'I hope you packed your lifejacket, Cadet.'
    else:
      yield 'Are you ready for the next mission?'
      yield 'I hope you\'re prepared for this one, Cadet.'
      yield 'Cadet, are you up for some more action?'

  def _success_openings(self) -> Iterable[str]:
    yield 'Well done!'
    yield 'Good job!'

  def _failure_openings(self) -> Iterable[str]:
    yield 'Oh, dear.'

  # Premise - only used in briefings, for flavor.
    
  def _premise(self) -> Iterable[str]:
    planner_kinds = collections.Counter()
    for p in self.cavern.conquest.somatic_planners:
      planner_kinds[type(p).__name__] += 1

    if planner_kinds['TreasureCavePlanner'] == 1:
      yield (
          'The Hognose scanner aboard the L.M.S. Explorer is picking up a '
          'nearby cavern filled with Energy Crystals.')
    elif planner_kinds['TreasureCavePlanner'] > 0:
      yield 'We have located a cave system with an abundance of Energy Crystals.'

  # Objectives - phrased differently for briefing, success, and failure.

  def _resource_objective(self) -> Optional[ResourceObjective]:
    for o in self.cavern.diorama.objectives:
      if isinstance(o, ResourceObjective):
        return o
    return None
  
  def _briefing_non_resource_objectives(self) -> Iterable[str]:
    yield 'build up your base'

  def _briefing_resource_objectives(self) -> Iterable[str]:
    o = self._resource_objective()
    if o:
      if o.crystals:
        yield f'{o.crystals} Energy Crystals'
      if o.ore:
        yield f'{o.ore} Ore'
      if o.studs:
        yield f'{o.studs} Building Studs'

  def _briefing_objective(self) -> str:
    nro = tuple(self._briefing_non_resource_objectives())
    ro = tuple(self._briefing_resource_objectives())
    if not ro:
      return _join_human(nro).capitalize()
    if len(ro) == 1:
      return _join_human(nro + (f'collect {ro[0]}',)).capitalize()
    return f'{_join_human(nro).capitalize()}, then collect {_join_human(ro)}'

def _join_human(things: Sequence[str]) -> str:
  if len(things) == 0:
    return ''
  if len(things) == 1:
    return things[0]
  return f'{", ".join(things[:-1])} and {things[-1]}'