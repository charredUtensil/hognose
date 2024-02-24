from typing import Tuple

import abc


class Hazard(abc.ABC):
  @property
  @abc.abstractmethod
  def serial_key(self) -> Tuple[float]:
    pass


class Erosion(Hazard):
  def __init__(self, cooldown: float, initial_delay: float):
    self.cooldown = cooldown
    self.initial_delay = initial_delay

  def __str__(self):
    return f'{self.cooldown:.0f}+{self.initial_delay:.0f}'

  @property
  def serial_key(self):
    return (self.cooldown, self.initial_delay)


Erosion.DEFAULT = Erosion(30, 10)


class Landslide(Hazard):
  def __init__(self, cooldown: float):
    self.cooldown = cooldown

  def __str__(self):
    return f'{self.cooldown:.0f}'

  @property
  def serial_key(self):
    return (self.cooldown,)


Landslide.DEFAULT = Landslide(30)
