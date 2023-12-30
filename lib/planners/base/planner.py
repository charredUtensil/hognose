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
  def pearl_radius(self):
    return min(min(bp.width, bp.height) for bp in self.baseplates) // 2

  def __str__(self):
    oyster = str(self.oyster) if hasattr(self, 'oyster') else None
    type_name = type(self).__name__
    ec = (
        f'{self.expected_crystals}EC'
        if hasattr(self, 'expected_crystals') and self.expected_crystals
        else None)
    ms = f'{self.monster_spawner}' if hasattr(self, 'monster_spawner') else None
    return ' '.join(
        s for s in (f'#{self.id}', oyster, type_name, ec, ms)
        if s is not None)