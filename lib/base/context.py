from typing import Optional

import enum

from .logger import Logger
from .pseudorandom import DiceBox, Rng, coerce_seed

class Biome(enum.Enum):
  ROCK = 'rock'
  ICE = 'ice'
  LAVA = 'lava'

class Context(object):

  def __init__(
      self,
      seed: str,
      logger: Optional[Logger]
      ):
    self.logger = logger or Logger()
    self.seed = coerce_seed(seed)
    self._rng = DiceBox(self.seed)
    rng = self._rng['init', -1]

    # Which biome the cave will use.
    # Affects some values used for rng later.
    self.biome = rng.uniform_choice(Biome)

    # The total number of bubbles to spawn.
    self.bubble_count            = 80
    # The radius to spawn bubbles in.
    self.bubble_spawn_radius     = 17
    # The largest possible bubble to generate.
    self.bubble_max_area         = 200

    # The number of bubbles to become "special".
    # The higher this number is, the more things will happen in the final map.
    self.special_baseplate_count = 20
    # The chance for each non-spanning connection to become a hallway.
    self.weave_chance            = 0.20

    # The min/max percentage of the cavern to fill.
    # Generation will fail if the sum of these two is >= 1
    self.water_coverage = {
      Biome.ROCK          : (0.00, 0.20),
      Biome.ICE           : (0.00, 0.60),
      Biome.LAVA          : (0.00, 0.10),
    }[self.biome]
    self.lava_coverage =  {
      Biome.ROCK          : (0.00, 0.10),
      Biome.ICE           : (0.00, 0.05),
      Biome.LAVA          : (0.10, 0.50),
    }[self.biome]

    # The chance for fluid to spread. Larger numbers here result in fewer,
    # longer rivers. Smaller numbers result in more individual lakes.
    self.water_spread            = 0.75
    self.lava_spread             = 0.30

    # The chance for a cave/hall with lava to spread erosion events.
    self.cave_erode_chance       = 0.37
    self.hall_erode_chance       = 0.60

    # How blobby caves/halls should be.
    # 0 results in perfect squashed octagons.
    # Larger values can result in oversized spaces or extremely jagged caves.
    self.cave_baroqueness        = 0.12
    self.hall_baroqueness        = 0.05

    # In approximately crystals per unit of perimeter caves should have,
    # How many crystals all caves get.
    self.base_richness           = 0.50
    # How many additional crystals caves furthest from spawn get.
    self.distance_richness       = 2.72
    # How many additional crystals caves later in generation get.
    self.completion_richness     = 1.00
    
    # The chance any arbitrary cave will have a recharge seam.
    # The spawn cave will always get one additional recharge seam.
    self.recharge_seam_chance = {
      Biome.ROCK                 : 0.07,
      Biome.ICE                  : 0.13,
      Biome.LAVA                 : 0.10,
    }[self.biome]

    # The likelihood each cave/hall will have landslides at all.
    self.cave_landslide_chance   = 0.40
    self.hall_landslide_chance   = 0.80
    # How many landslides per minute per unit of perimeter.
    self.cave_landslide_freq     = 0.50
    self.hall_landslide_freq     = 1.20

    # For maps with no special objective, what percentage of total crystals
    # must be collected as a goal. Rock Radiers levels tend to be about 20%.
    self.crystal_goal_ratio      = 0.20

  def __str__(self):
    return f'seed: 0x{self.seed:08x}'

  @property
  def rng(self) -> DiceBox:
    return self._rng