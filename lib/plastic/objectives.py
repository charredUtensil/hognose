import abc

from .miners import Miner

class Objective(abc.ABC):
  
  @abc.abstractmethod
  def serialize(self) -> str:
    pass

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