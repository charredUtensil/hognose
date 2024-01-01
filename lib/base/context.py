from typing import NamedTuple, Optional

import enum

from .logger import Logger
from .pseudorandom import DiceBox, Rng, coerce_seed

class Biome(enum.Enum):
  ROCK = 'rock'
  ICE = 'ice'
  LAVA = 'lava'

# Scale values so caves have higher risk and reward away from spawn
Curve = NamedTuple(
    'Curve',
    base=float,       # The value for the spawn cave
    hops=float,       # Scales a % of maximum hops from spawn
    completion=float  # Scales as a % of total caves conquered
    )

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
    self.biome: Biome = rng.uniform_choice(Biome)

    # Does this cave have monsters?
    self.has_monsters = rng.chance(0.75)

    self.size = rng.uniform_int(min=50, max=80)

    # Each time a bubble is generated, it may be at most this percent of the
    # remaining area allowed.
    self.baseplate_max_area              = 300
    self.baseplate_max_oblongness        = 2

    # The maximum number of times to run the separate step.
    # Separation is a physics simulation that is not guaranteed to halt, so
    # after this many steps, delete any bubble that's still moving and print a
    # warning.
    self.max_separate_steps              = 75

    # The number of bubbles to become "special".
    # The higher this number is, the more things will happen in the final map.
    self.special_baseplate_ratio         = 0.28
    # The ratio of non-spanning connections that become hallways.
    self.weave_ratio                     = 0.16

    # The min/max percentage of the cavern to fill.
    # Generation will fail if the sum of these two is >= 1
    self.water_coverage = {
      Biome.ROCK                  : (0.00, 0.20),
      Biome.ICE                   : (0.00, 0.60),
      Biome.LAVA                  : (0.00, 0.10),
    }[self.biome]
    self.lava_coverage =  {
      Biome.ROCK                  : (0.00, 0.10),
      Biome.ICE                   : (0.00, 0.05),
      Biome.LAVA                  : (0.10, 0.50),
    }[self.biome]

    # The chance for fluid to spread. Larger numbers here result in fewer,
    # longer rivers. Smaller numbers result in more individual lakes.
    # Does not affect the total water or lava in the cavern.
    self.water_spread                    = 0.75
    self.lava_spread                     = 0.30

    # The chance for a cave/hall with lava or erosion to spread erosion to
    # its neighbors.
    self.cave_erode_chance               = 0.37
    self.hall_erode_chance               = 0.60

    # How blobby caves/halls should be.
    # 0 results in perfect squashed octagons.
    # Larger values can result in oversized spaces or extremely jagged caves.
    self.cave_baroqueness                = 0.12
    self.hall_baroqueness                = 0.05

    # Crystals per unit of perimeter caves should have
    self.crystal_richness = Curve(
                                           0.50,
                                           1.00,
                                           1.00,
    )

    # Monsters to spawn per minute per cave
    self.monster_spawn_rate = Curve(
                                           0.30,
                                           0.56,
                                           0.60,
    )

    # How many monsters to spawn at a time
    self.monster_wave_size = Curve(
                                           1.75,
                                           2.00,
                                           3.00,
    )
    
    # The chance any arbitrary cave will have a recharge seam.
    # The spawn cave will always get one additional recharge seam.
    self.recharge_seam_chance = {
      Biome.ROCK                         : 0.07,
      Biome.ICE                          : 0.13,
      Biome.LAVA                         : 0.10,
    }[self.biome]

    # The likelihood each cave/hall will have landslides at all.
    self.cave_landslide_chance           = 0.40
    self.hall_landslide_chance           = 0.80
    # How many landslides per minute per unit of perimeter.
    self.cave_landslide_freq             = 0.50
    self.hall_landslide_freq             = 1.20
    # The shortest time allowed between landslides.
    self.min_landslide_period            = 15.0

    # For maps with no special objective, what percentage of total crystals
    # must be collected as a goal. Rock Radiers levels tend to be about 20%.
    self.crystal_goal_ratio              = 0.20

  def __str__(self):
    def h():
      yield f'seed:         0x{self.seed:08x}'
      yield f'biome:        {self.biome}'
      yield f'has monsters: {"yes" if self.has_monsters else "no"}'
      yield f'target size:  {self.size}x{self.size}'
    return '\n'.join(h())

  @property
  def rng(self) -> DiceBox:
    return self._rng