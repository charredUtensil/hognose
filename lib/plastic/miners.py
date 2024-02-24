from typing import Iterable, Literal, Optional, Tuple

import math
import enum

from .entities import Entity
from .position import Position


class Miner(Entity):

  class Unique(enum.Enum):
    OFFICER = 'OFFICER'
    AXLE = 'Axle'
    BANDIT = 'Bandit'
    CHIEF = 'Chief'
    DOCS = 'Docs'
    JET = 'Jet'
    SPARKS = 'Sparks'

  class Loadout(enum.Enum):
    DRILL = 'Drill'
    JOB_EXPLOSIVES_EXPERT = 'JobExplosivesExpert'
    JOB_DRIVER = 'JobDriver'
    JOB_PILOT = 'JobPilot'
    JOB_ENGINEER = 'JobEngineer'
    JOB_GEOLOGIST = 'JobGeologist'
    JOB_SAILOR = 'JobSailor'

  def __init__(
      self,
      id: int,
      position: Position,
      unique: Optional[Unique] = None,
      loadout: Iterable[Loadout] = (Loadout.DRILL,),
      level: Literal[1, 2, 3, 4, 5] = 1,
      essential: bool = False):
    super().__init__(position)
    self.id = id
    self.unique = unique
    self.loadout = frozenset(loadout)
    self.level = level
    self.essential = essential

  def serialize(self, offset: Tuple[int, int]):
    def h():
      yield f'ID={self.id:d}'
      if self.unique:
        yield f'/{self.unique.value}'
      yield ','
      yield self.position.serialize(offset, math.pi / 2)
      yield ','
      for v in sorted(l.value for l in self.loadout):
        yield f'{v}/'
      for _ in range(self.level - 1):
        yield 'Level/'
      if self.essential:
        yield ',Essential=true'
    return ''.join(h())
