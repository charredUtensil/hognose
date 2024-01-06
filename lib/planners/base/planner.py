from typing import Iterable, Literal, Optional, Tuple

import abc

from lib.base import ProceduralThing
from lib.outlines import Baseplate
from lib.plastic import Tile

class Planner(ProceduralThing, abc.ABC):

  def __init__(self, id, context):
    super().__init__(id, context)

  @property
  @abc.abstractmethod
  def baseplates(self) -> Tuple[Baseplate]:
    pass

  @property
  def center(self) -> Tuple[float, float]:
    bp_ct = len(self.baseplates)
    if bp_ct % 2 == 1:
      return self.baseplates[bp_ct // 2].center
    else:
      ci = bp_ct // 2
      cx1, cy1 = self.baseplates[ci - 1].center
      cx2, cy2 = self.baseplates[ci].center
      return (cx1 + cx2) / 2, (cy1 + cy2) / 2

  @property
  @abc.abstractmethod
  def pearl_radius(self):
    pass

  def __str__(self):
    def h():
      yield f'#{self.id}'
      if hasattr(self, 'oyster'):
        yield str(self.oyster)
      yield type(self).__name__
      yield f'R{self.pearl_radius}'
      if hasattr(self, 'expected_crystals') and self.expected_crystals:
        f'{self.expected_crystals}EC'
      if hasattr(self, 'monster_spawner'):
        f'{self.monster_spawner}'
    return ' '.join(h())