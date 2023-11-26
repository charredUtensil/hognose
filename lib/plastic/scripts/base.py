from typing import Tuple

import abc

class ScriptElement(abc.ABC):

  @abc.abstractmethod
  def serialize(self, offset: Tuple[int, int]) -> str:
    pass