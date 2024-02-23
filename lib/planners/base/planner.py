from typing import Tuple

import abc

from lib.base import ProceduralThing
from lib.outlines import Baseplate


class Planner(ProceduralThing, abc.ABC):

  @property
  @abc.abstractmethod
  def baseplates(self) -> Tuple[Baseplate]:
    pass

  @property
  def center(self) -> Tuple[float, float]:
    bp_ct = len(self.baseplates)
    if bp_ct % 2 == 1:
      return self.baseplates[bp_ct // 2].center
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
      # pylint: disable=no-member
      if hasattr(self, 'expected_crystals') and self.expected_crystals:
        yield f'{self.expected_crystals}EC'
      if hasattr(self, 'monster_spawner'):
        yield f'{self.monster_spawner}'
    return ' '.join(h())
