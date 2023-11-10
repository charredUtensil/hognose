from typing import Optional

from .logger import Logger
from .seeder import Seeder
from .thing_random import ThingRandom

class Context(object):

  def __init__(
      self,
      seed: str,
      logger: Optional[Logger]
      ):
    self.logger = logger or Logger()
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

    self.base_richness         = 0.50
    self.hop_richness          = 4.00

    self.cave_baroqueness      = 0.12
    self.hall_baroqueness      = 0.05

    self.recharge_seam_chance  = 0.07
    self.cave_has_landslides_chance = 0.40
    self.cave_landslides       = 0.20
    self.hall_has_landslides_chance = 0.60
    self.hall_landslides       = 0.40

    self.crystal_goal_ratio    = 0.20

  def __str__(self):
    return f'seed:0x{self.seed:08x}'

  def rng(self, id: int) -> ThingRandom:
    return self._seeder.rng(self.stage, id)