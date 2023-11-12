from typing import Iterable, Literal, Optional, Tuple, TypeVar

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
  'conquest.differentiate',
  'rough.pearl',
  'fine.place_crystals',
  'flood',
  'init',
  'lore',
  'conquest.expected_crystals',
  'fine.place_recharge_seam',
  'fine.place_landslides',
)

class Rng(object):
  """Produces pseudorandom values. A wrapper for NumPy's Rng."""

  def __init__(self, seed: int):
    self._rng = np.random.default_rng(seed)

  def random(self) -> float:
    """A uniform random float between 0 and 1"""
    return self._rng.random()

  def bid(self, bids: Iterable[Tuple[float, T]]) -> T:
    """Given tuples of (bid, item), choose an item.
    Higher bids are more likely to be chosen."""
    bids = tuple(b for b in bids if b[0] > 0)
    n = self._rng.random() * sum(bid for (bid, _) in bids)
    for bid, result in bids:
      n -= bid
      if n <= 0:
        return result
    return bids[-1][1]

  def choice(self, choices: Iterable[T]) -> T:
    """A uniformly random choice of one of the given items."""
    c = tuple(choices)
    return c[self._rng.integers(0, len(c))]

  def normal(self, mean: float = 0, stddev: float = 1) -> float:
    """A randomly chosen number with a normal distribution."""
    return self._rng.normal(loc=mean, scale=stddev)

  def pareto(self, shape: float, mode: float) -> float:
    """A randomly chosen number with a Pareto distribution."""
    return self._rng.pareto(shape) * mode

  def point_in_circle(
      self, radius: float, origin: Tuple[float, float] = (0, 0)
      ) -> Tuple[float, float]:
    """A uniformly random point in a circle with the given radius."""
    t = self._rng.random() * 2 * math.pi
    u = self._rng.random() + self._rng.random()
    r = 2 - u if u > 1 else u
    return (
        radius * r * math.cos(t) + origin[0],
        radius * r * math.sin(t) + origin[1])

class DiceBox(object):

  def __init__(self, seed: int):
    main_rng = np.random.default_rng(seed)
    self._seeds = {
        kind: main_rng.integers(0, MAX_SEED)
        for kind in KINDS}
    self._rng: Dict[Tuple[Literal[KINDS], int], Rng] = {}

  def __getitem__(self, index: Tuple[Literal[KINDS], int]) -> Rng:
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

  # Anything else: Take bits from the MD5 hash of the given phrase
  md5 = hashlib.md5()
  md5.update(seed.encode('utf-8'))
  return int(md5.hexdigest()[:8], 16) % MAX_SEED