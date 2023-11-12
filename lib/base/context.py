from typing import Optional

from .logger import Logger
from .pseudorandom import DiceBox, Rng, coerce_seed

class Context(object):

  def __init__(
      self,
      seed: str,
      logger: Optional[Logger]
      ):
    self.logger = logger or Logger()
    self.seed = coerce_seed(seed)
    self._rng = DiceBox(self.seed)

    self.bubble_count          = 80
    self.bubble_radius         = 17
    self.bubble_area_mode      = 30
    
    self.cave_count            = 20
    self.weave_chance          = 0.20

    self.water_level           = 0.20
    self.water_spread          = 0.75
    self.lava_level            = 0.06
    self.lava_spread           = 0.30

    self.cave_erode_chance     = 0.37
    self.hall_erode_chance     = 0.60

    self.cave_baroqueness      = 0.12
    self.hall_baroqueness      = 0.05

    self.base_richness         = 0.50
    self.hop_richness          = 4.00
    
    self.recharge_seam_chance  = 0.07

    self.cave_landslide_chance = 0.40
    self.cave_landslide_freq   = 0.50
    self.hall_landslide_chance = 0.80
    self.hall_landslide_freq   = 1.20

    self.crystal_goal_ratio    = 0.20

  def __str__(self):
    return f'seed:0x{self.seed:08x}'

  @property
  def rng(self) -> DiceBox:
    return self._rng