from typing import Iterable

import abc

from .miners import Miner

class Objective(abc.ABC):
  
  @abc.abstractmethod
  def serialize(self) -> str:
    pass

  @staticmethod
  def uniq(objectives: Iterable['Objective']) -> Iterable['Objective']:
    crystals = 0
    ore = 0
    studs = 0
    for o in objectives:
      if isinstance(o, ResourceObjective):
        crystals = max(crystals, o.crystals)
        ore = max(ore, o.ore)
        studs = max(studs, o.studs)
      else:
        yield o
    if crystals or ore or studs:
      yield ResourceObjective(crystals, ore, studs)

class FindMinerObjective(Objective):

  def __init__(self, miner: Miner):
    self.miner = miner

  def serialize(self):
    return f'findminer:{self.miner.id:d}'

class ResourceObjective(Objective):

  def __init__(self, crystals, ore=0, studs=0):
    self.crystals = crystals
    self.ore = ore
    self.studs = studs

  def serialize(self):
    return f'resources: {self.crystals:d},{self.ore:d},{self.studs:d}'

class VariableObjective(Objective):

  def __init__(self, part:str):
    self.part = part

  def serialize(self):
    return f'variable:{self.part}'