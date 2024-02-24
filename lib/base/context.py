from typing import NamedTuple, Tuple, TypeVar

import dataclasses
import enum

from lib.base.logger import Logger
from lib.base.pseudorandom import DiceBox

T = TypeVar('T')


class Biome(enum.Enum):
  """A biome for the level."""
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


@dataclasses.dataclass(frozen=True)
class Context(): # pylint: disable=too-many-instance-attributes
  """A collection of constants used in level generation."""
  logger: Logger
  seed: int
  rng: DiceBox

  # Which biome the cave will use.
  # Affects some values used for rng later.
  biome: Biome

  # Does this cave have monsters?
  has_monsters: bool

  # The "target" final size for the cavern. Final size may be larger or
  # smaller due to randomness. Larger caverns will not be cropped.
  size: int

  # Each time a bubble is generated, it may be at most this percent of the
  # remaining area allowed.
  baseplate_max_side_ratio: float
  baseplate_max_oblongness: float

  # The number of bubbles to become "special".
  # The higher this number is, the more "busy" the final map will be.
  special_baseplate_count: int

  # The ratio of non-spanning connections that become hallways.
  weave_ratio: float

  # The min/max percentage of the cavern to fill.
  # Generation will fail if the sum of these two is >= 1
  water_coverage: Tuple[float, float]
  lava_coverage: Tuple[float, float]

  # The chance for fluid to spread. Larger numbers here result in fewer,
  # longer rivers. Smaller numbers result in more individual lakes.
  # Does not affect the total water or lava in the cavern.
  water_spread: float
  lava_spread: float

  # The chance for a cave/hall with lava or erosion to spread erosion to
  # its neighbors.
  cave_erode_chance: float
  hall_erode_chance: float

  # How blobby caves/halls should be.
  # 0 results in perfect squashed octagons.
  # Larger values can result in oversized spaces or extremely jagged caves.
  cave_baroqueness: float
  hall_baroqueness: float

  # Crystals per unit of perimeter caves should have
  crystal_richness: Curve

  # Extra ore per unit of perimeter caves should have
  # Note this does not include the 4 ore recovered by clearing rubble.
  ore_richness: Curve

  # Monsters to spawn per minute per cave
  monster_spawn_rate: Curve

  # How many monsters to spawn at a time
  monster_wave_size: Curve

  # The chance any arbitrary cave will have a recharge seam.
  # Some caves (including the spawn cave) ignore this and always have one.
  recharge_seam_chance: float

  # The likelihood each cave/hall will have landslides at all.
  cave_landslide_chance: float
  hall_landslide_chance: float

  # How many landslides per minute per unit of perimeter.
  cave_landslide_freq: float
  hall_landslide_freq: float

  # The shortest time allowed between landslides.
  min_landslide_period: float

  # For maps with no special objective, what percentage of total crystals
  # must be collected as a goal. Rock Radiers levels tend to be about 20%.
  crystal_goal_ratio: float

  def __str__(self):
    def h():
      yield f'seed: 0x{self.seed:08x}'
      yield f'biome: {self.biome}'
      yield f'has monsters: {"yes" if self.has_monsters else "no"}'
      yield f'target size: {self.size}x{self.size}'
    return '\n'.join(h())

  @classmethod
  def coerce_overrides(cls, overrides):
    #types = {f.name: f.type for f in dataclasses.fields(cls)}

    def h():
      for k, v in overrides.items():
        yield k, v
    return {h()}

  @classmethod
  def generate(cls, logger: Logger, seed: int, **overrides):
    dice_box = DiceBox(seed)
    rng = dice_box['init', -1]

    biome = rng.uniform_choice(Biome)
    if 'biome' in overrides:
      biome = overrides[biome]

    def for_biome(rock: T, ice: T, lava: T) -> T:
      if biome == Biome.ROCK:
        return rock
      if biome == Biome.ICE:
        return ice
      return lava

    has_monsters = rng.chance(0.75)
    target_size = rng.uniform_int(min=50, max=80)

    kwargs = {
      'logger': logger,
      'seed': seed,
      'rng': dice_box,
      'biome': biome,
      'has_monsters': has_monsters,
      'size': target_size,
      'baseplate_max_side_ratio': 0.33,
      'baseplate_max_oblongness': 3,
      'special_baseplate_count': 20,
      'weave_ratio': 0.21,
      'water_coverage': for_biome(
          (0.00, 0.20),
          (0.00, 0.60),
          (0.00, 0.10)),
      'lava_coverage': for_biome(
          (0.00, 0.10),
          (0.00, 0.05),
          (0.10, 0.50)),
      'water_spread': 0.75,
      'lava_spread': 0.15,
      'cave_erode_chance': 0.37,
      'hall_erode_chance': 0.60,
      'cave_baroqueness': 0.12,
      'hall_baroqueness': 0.05,
      'crystal_richness': Curve(0.50, 1.00, 1.00),
      'ore_richness': Curve(3.75, -0.50, -0.25),
      'monster_spawn_rate': Curve(0.30, 0.56, 0.60),
      'monster_wave_size': Curve(1.75, 2.00, 3.00),
      'recharge_seam_chance': for_biome(0.07, 0.13, 0.10),
      'cave_landslide_chance': 0.40,
      'hall_landslide_chance': 0.80,
      'cave_landslide_freq': 0.50,
      'hall_landslide_freq': 1.20,
      'min_landslide_period': 15.0,
      'crystal_goal_ratio': 0.20,
    }

    kwargs.update(overrides)

    return cls(**kwargs)
