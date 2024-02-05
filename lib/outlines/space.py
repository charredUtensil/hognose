"""Base class for a single rectangle in the map area."""

from typing import Tuple

import abc

from lib.base import ProceduralThing


class Space(ProceduralThing):
  """Base class for a single rectangle in the map area."""

  @property
  def area(self):
    return self.width * self.height

  @property
  @abc.abstractmethod
  def width(self) -> float:
    pass

  @property
  @abc.abstractmethod
  def height(self) -> float:
    pass

  @property
  @abc.abstractmethod
  def center(self) -> Tuple[float, float]:
    pass
