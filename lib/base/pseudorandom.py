from typing import Dict, Iterable, Literal, Optional, Tuple, TypeVar

T = TypeVar("T")

import hashlib
import math
import numpy as np
import random
import re
import time

MAX_SEED = 0x8000_0000

KINDS = (
  # Anything using random numbers must be listed here.
  # If new steps are added, append them to this list
  # to minimize disruption to existing caverns.
  'bubble',
  'weave',
  'differentiate',
  'rough.pearl',
  'fine.place_crystals',
  'flood',
  'init',
  'lore',
  'conquest.expected_crystals',
  'fine.place_recharge_seam',
  'fine.place_landslides',
  'fine.place_entities',
  'monster_spawner',
  'pick_spawn_cave',
)

class Rng(object):
  """Produces pseudorandom values. A wrapper for NumPy's Rng."""

  def __init__(self, seed: int):
    self._rng = np.random.default_rng(seed)

  def chance(
      self,
      chance: float) -> bool:
    return self._rng.random() < chance

  def uniform(
      self,
      min: float = 0,
      max: float = 1) -> float:
    return self._rng.random() * (max - min) + min

  def uniform_int(self, *args, **kwargs) -> int:
    return math.floor(self.uniform(*args, **kwargs))

  def beta(
      self,
      a: float = 5,
      b: float = 5,
      min: float = 0,
      max: float = 1) -> float:
    """Use a beta distribution to choose a value between min and max.
    This is incredibly useful, since it is strictly bounded and many different
    curve shapes can be achieved by changing a and b.
    See https://eurekastatistics.com/beta-distribution-pdf-grapher/
    """
    return self._rng.beta(a, b) * (max - min) + min

  def beta_int(self, *args, **kwargs) -> int:
    return math.floor(self.beta(*args, **kwargs))

  def uniform_point_in_circle(
      self,
      radius: float,
      origin: Tuple[float, float] = (0, 0)
      ) -> Tuple[float, float]:
    """A uniformly random point in a circle with the given radius."""
    t = self._rng.random() * 2 * math.pi
    u = self._rng.random() + self._rng.random()
    r = 2 - u if u > 1 else u
    return (
        radius * r * math.cos(t) + origin[0],
        radius * r * math.sin(t) + origin[1])

  def beta_choice(self, choices: Iterable[T], a: float = 5, b: float = 5) -> T:
    """Use a beta distribution to choose one of the given items."""
    c = tuple(choices)
    return c[math.floor(self._rng.beta(a, b) * len(c))]

  def uniform_choice(self, choices: Iterable[T]) -> T:
    """A uniformly random choice of one of the given items."""
    c = tuple(choices)
    return c[self._rng.integers(0, len(c))]

  def weighted_choice(self, bids: Iterable[Tuple[float, T]]) -> T:
    """Given tuples of (weight, item), choose an item.
    Higher weights are more likely to be chosen."""
    bids = tuple(b for b in bids if b[0] > 0)
    n = self._rng.random() * sum(w for (w, _) in bids)
    for w, result in bids:
      n -= w
      if n <= 0:
        return result
    return bids[-1][1]

class DiceBox(object):

  def __init__(self, seed: int):
    main_rng = np.random.default_rng(seed)
    self._seeds = {
        kind: main_rng.integers(0, MAX_SEED)
        for kind in KINDS}
    self._rng: Dict[Tuple[str, int], Rng] = {}

  def __getitem__(self, index: Tuple[str, int]) -> Rng:
    if index not in self._rng:
      # To get the seed for this specific RNG, just shift it by a fixed amount.
      # 1999 is an arbitrarily chosen constant.
      seed = (self._seeds[index[0]] + index[1] * 1999) % MAX_SEED
      self._rng[index] = Rng(np.random.default_rng(seed))
    return self._rng[index]

def coerce_seed(seed: Optional[str]) -> int:
  """Coerces the given seed into a number that is an acceptable seed."""
  # No seed: Use seconds since epoch
  if seed is None:
    return int(time.time()) % MAX_SEED

  # Seed that looks like a hex number: use that as seed
  m = re.match(r'\A\s*(0x)?(?P<seed>[0-9a-fA-F]{1,8})\s*\Z', seed)
  if m:
    return int(m.group('seed'), 16)

  # Seed that looks like a level name: extract seed
  m = re.match(
      r'\A\s*((HN-?)?[KEA])?'
      r'(?P<a>[0-9a-fA-F]{3})-?'
      r'(?P<b>[0-9a-fA-F]{5})\s*\Z', seed)
  if m:
    return int(f'{m.group("a")}{m.group("b")}', 16)

  # Anything else: Take bits from the MD5 hash of the given phrase
  md5 = hashlib.md5()
  md5.update(seed.encode('utf-8'))
  return int(md5.hexdigest()[:8], 16) % MAX_SEED