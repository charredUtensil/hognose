from typing import Tuple

import abc
import math
import random

class Space(abc.ABC):

  def area(self):
    return self.width * self.height

  @property
  @abc.abstractmethod
  def left(self) -> float:
    pass

  @property
  @abc.abstractmethod
  def top(self) -> float:
    pass

  @property
  @abc.abstractmethod
  def right(self) -> float:
    pass

  @property
  @abc.abstractmethod
  def bottom(self) -> float:
    pass

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