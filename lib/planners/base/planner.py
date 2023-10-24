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