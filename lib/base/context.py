from typing import Optional

from .logger import Logger
from .seeder import Seeder
from .thing_random import ThingRandom

class Context(object):

  def __init__(
      self,
      seed: str,
      logger: Optional[Logger]=None
      ):
    self.logger = logger or Logger.VOID
    self.seed = Seeder.coerce_seed(seed)
    self._seeder = Seeder(self.seed)
    self.stage = 'init'

    self.bubble_count          = 80
    self.bubble_radius         = 17
    self.bubble_area_mode      = 30

    self.auxiliary_edge_chance = 0.20
    self.special_lot_ratio     = 0.25

    self.water_level           = 0.20
    self.water_spread          = 0.75
    self.lava_level            = 0.06
    self.lava_spread           = 0.30

    self.cave_baroqueness      = 0.12

  def __str__(self):
    return f'seed:0x{self.seed:08x}'

  def rng(self, id: int) -> ThingRandom:
    return self._seeder.rng(self.stage, id)