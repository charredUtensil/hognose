from typing import Iterable, Literal, Optional, Tuple

import enum

from .position import Position

class Miner(object):

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
      pos: Tuple[float, float],
      facing: float,
      unique: Optional[Unique] = None,
      loadout: Iterable[Loadout] = [Loadout.DRILL],
      level: Literal[1,2,3,4,5] = 1,
      essential: bool = False): 
    self.id = id
    self.x, self.y = pos
    self.facing = facing
    self.unique = unique
    self.loadout = frozenset(loadout)
    self.level = level
    self.essential = essential

  def serialize(self, offset: Tuple[int, int]):
    position = Position(
      (self.x + 0.5, self.y + 0.5, 0),
      (0, self.facing, 0)
    )
    def h():
      yield f'ID={self.id:d}'
      if self.unique:
        yield f'/{self.unique.value}'
      yield ','
      yield position.serialize(offset)
      yield ','
      for n in sorted(self.loadout):
        yield f'{n.value}/'
      for _ in range(self.level - 1):
        yield 'Level/'
      if self.essential:
        yield ',Essential=true'
    return ''.join(h())