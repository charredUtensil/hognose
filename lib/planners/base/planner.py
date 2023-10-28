from typing import Iterable, Tuple

import abc

from lib.base import ProceduralThing
from lib.outlines import Baseplate

class Planner(ProceduralThing, abc.ABC):

  def __init__(self, id, context, baseplates: Iterable[Baseplate]):
    super().__init__(id, context)
    self._baseplates = tuple(baseplates)
    self.expected_crystals: int = 0

  @property
  def baseplates(self) -> Tuple[Baseplate]:
    return self._baseplates

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

  def __str__(self):
    return f'{type(self).__name__} #{self.id}'