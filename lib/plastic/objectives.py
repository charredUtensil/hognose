from typing import Iterable

import abc

from .miners import Miner


class Objective(abc.ABC):

  @abc.abstractmethod
  def serialize(self) -> str:
    pass

  @property
  @abc.abstractmethod
  def description(self) -> str:
    pass


class ResourceObjective(Objective):

  def __init__(self, crystals, ore=0, studs=0):
    self.crystals = crystals
    self.ore = ore
    self.studs = studs

  @property
  def description(self):
    def h():
      if self.crystals:
        yield f'{self.crystals:d} EC'
      if self.ore:
        yield f'{self.ore:d} Ore'
      if self.studs:
        yield f'{self.studs:d} Studs'
    return f'Collect {" ".join(h())}'

  def serialize(self):
    return f'resources: {self.crystals:d},{self.ore:d},{self.studs:d}'


class VariableObjective(Objective):

  def __init__(self, condition, description):
    self._condition: str = condition
    self._description: str = description

  @property
  def description(self):
    return self._description

  def serialize(self):
    return f'variable:{self._condition}/{self._description}'
