import abc

class Hazard(abc.ABC):
  @property
  @abc.abstractmethod
  def serial_key(self) -> str:
    pass

class Erosion(Hazard):
  def __init__(self, cooldown: float, initial_delay: float):
    self.cooldown = cooldown
    self.initial_delay = initial_delay

  @property
  def serial_key(self):
    return f'{self.cooldown:0.1f}/{self.initial_delay:0.1f}'

Erosion.DEFAULT = Erosion(30, 10)

class Landslide(Hazard):
  def __init__(self, cooldown: float):
    self.cooldown = cooldown

  @property
  def serial_key(self):
    return f'{self.cooldown:0.1f}'

Landslide.DEFAULT = Landslide(30)