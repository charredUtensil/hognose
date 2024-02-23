from typing import Iterable, List, NamedTuple, Optional, Tuple, TYPE_CHECKING

import math

from lib.base import Context
from lib.plastic import (
    Diorama, ResourceObjective, Script, ScriptFragment, VariableObjective)

if TYPE_CHECKING:
  from lib.lore import Lore

MinersInfo = NamedTuple(
    'MinersInfo', pos=Tuple[int, int], miners_count=int, caves_count=int)
HqInfo = NamedTuple('HqInfo', pos=Tuple[int, int], description=str)

PREFIX = 'adjurator_'


class Adjurator():

  VAR_FOUND_HQ = f'{PREFIX}foundHq'
  VAR_FOUND_ALL_LOST_MINERS = f'{PREFIX}foundAllLostMiners'
  VAR_LOST_MINERS_COUNT = f'{PREFIX}lostMiners'
  ON_FOUND_ALL_LOST_MINERS = f'{PREFIX}onFoundAllLostMiners'

  def __init__(self, context: Context):
    self._context = context
    self._crystals = 0
    self._ore = 0
    self._studs = 0
    self._hq: Optional[HqInfo] = None
    self._miners: List[MinersInfo] = []

  @property
  def crystals(self):
    return self._crystals

  @property
  def ore(self):
    return self._ore

  @property
  def studs(self):
    return self._studs

  @property
  def lost_miners(self):
    return sum(info.miners_count for info in self._miners)

  @property
  def lost_miner_caves(self):
    return sum(info.caves_count for info in self._miners)

  @property
  def positions(self) -> Iterable[Tuple[int, int]]:
    if self._hq:
      yield self._hq.pos
    yield from (info.pos for info in self._miners)

  def collect_crystals(self, count: int):
    self._crystals = max(self._crystals, count)

  def collect_ore(self, count: int):
    self._ore = max(self._ore, count)

  def collect_studs(self, count: int):
    self._studs = max(self._studs, count)

  def find_hq(self, pos, message):
    self._hq = HqInfo(pos, message)

  def find_miners(self, pos, count):
    self._miners.append(MinersInfo(pos, count, 1))

  @property
  def _find_miners_message(self):
    miners = self.lost_miners
    if miners == 1:
      return 'Find the lost Rock Raider'
    caves = self.lost_miner_caves
    if caves == 1:
      return 'Find the cave with the lost Rock Radiers'
    return f'Find {miners} lost Rock Raiders'

  def _objectives(self):
    if self._hq:
      yield VariableObjective(
          f'{Adjurator.VAR_FOUND_HQ}>0',
          self._hq.description)
    if self._miners:
      yield VariableObjective(
          f'{Adjurator.VAR_FOUND_ALL_LOST_MINERS}>0',
          self._find_miners_message)
    if self._crystals or self._ore or self._studs:
      yield ResourceObjective(
          crystals=self._crystals,
          ore=self._ore,
          studs=self._studs)

  def write(self, diorama: Diorama):
    if not self._miners:
      # If the objectives aren't sufficient, pick a reasonable crystal goal.
      self._crystals = math.floor(
          diorama.crystal_yield * self._context.crystal_goal_ratio)
      self._crystals -= (self._crystals % 5)
    diorama.objectives.extend(self._objectives())

  def __str__(self):
    return 'Adjurator (Mission Objectives)'

  def script(self, diorama: Diorama, lore: 'Lore') -> ScriptFragment:
    del diorama
    def h():
      if self._hq:
        yield '# Objective: Find HQ'
        yield f'int {Adjurator.VAR_FOUND_HQ}=0'
      if self._miners:
        yield '# Objective: Find lost miners'
        yield f'int {Adjurator.VAR_FOUND_ALL_LOST_MINERS}=0'
        yield f'int {Adjurator.VAR_LOST_MINERS_COUNT}={self.lost_miners:d}'
        msg = Script.escape_string(lore.event_found_all_lost_miners)
        yield f'string {PREFIX}foundAllLostMinersMessage="{msg}"'
        yield f'{Adjurator.ON_FOUND_ALL_LOST_MINERS}::;'
        yield f'msg:{PREFIX}foundAllLostMinersMessage;'
        yield 'wait:3;'
        yield f'{Adjurator.VAR_FOUND_ALL_LOST_MINERS}=1;'
        yield ''
      yield ''
    return ScriptFragment(h())
