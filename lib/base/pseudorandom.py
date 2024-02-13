"""Base module for prng."""

from typing import Dict, Iterable, Optional, Tuple, TypeVar, Union

import hashlib
import math
import re
import time

import numpy as np

T = TypeVar('T')

# 2 billion levels ought to be enough for anyone.
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
  'place_buildings',
  'expected_ore',
  'place_ore',
)


class Rng():
  """
  Produces a single stream of pseudorandom values.

  This is mostly a convenience wrapper for NumPy's Rng.
  """
  # pylint: disable=redefined-builtin

  def __init__(self, seed: int):
    self._rng = np.random.default_rng(seed)

  # Random bool

  def chance(
          self,
          chance: float) -> bool:
    """
    Randomly returns True or False.

    chance: The probability this will return True.
    """
    return self._rng.random() < chance

  # Random float

  def uniform(
          self,
          min: float = 0,
          max: float = 1) -> float:
    """Returns a uniformly random value between min and max."""
    return self._rng.random() * (max - min) + min

  def beta(
      self,
      a: float = 5,
      b: float = 5,
      min: float = 0,
          max: float = 1) -> float:
    """
    Returns a random value between min and max using a beta distribution.

    A beta distribution is very useful here, since it has strict bounds on its
    return value, and many different curve shapes can be achieved by adjusting
    a and b.
    See https://eurekastatistics.com/beta-distribution-pdf-grapher/ to
    preview those curves.
    """
    return self._rng.beta(a, b) * (max - min) + min

  # Random int

  def uniform_int(self, *args, **kwargs) -> int:
    """Returns a uniformly random integer between min and max."""
    return math.floor(self.uniform(*args, **kwargs))

  def beta_int(self, *args, **kwargs) -> int:
    """
    Returns a random integer between min and max using a beta distribution.
    """
    return math.floor(self.beta(*args, **kwargs))

  # Random pair of floats

  def uniform_point_in_circle(
      self,
      radius: float,
      origin: Tuple[float, float] = (0, 0)
  ) -> Tuple[float, float]:
    """Returns a uniformly random point in a given circle."""
    t = self._rng.random() * 2 * math.pi
    u = self._rng.random() + self._rng.random()
    r = 2 - u if u > 1 else u
    return (
        radius * r * math.cos(t) + origin[0],
        radius * r * math.sin(t) + origin[1])

  # Random item from a list

  def uniform_choice(self, choices: Iterable[T]) -> T:
    """Returns a uniformly random item from the given choices."""
    c = tuple(choices)
    return c[self._rng.integers(0, len(c))]

  def beta_choice(self, choices: Iterable[T], a: float = 5, b: float = 5) -> T:
    """Returns a random item from the given choices using a beta distribution."""
    c = tuple(choices)
    return c[math.floor(self._rng.beta(a, b) * len(c))]

  def weighted_choice(self, bids: Iterable[Tuple[float, T]]) -> T:
    """
    Given tuples of (weight, item), returns an item.
    The probability that any item is chosen is its weight divided by the total
    weight of all items.
    """
    bids = tuple(b for b in bids if b[0] > 0)
    n = self._rng.random() * sum(w for (w, _) in bids)
    for w, result in bids:
      n -= w
      if n <= 0:
        return result
    return bids[-1][1]

  # Randomly shuffled list

  def shuffle(self, choices: Iterable[T]) -> Iterable[T]:
    """Returns a shuffled copy of the given choices."""
    result = list(choices)
    self._rng.shuffle(result)
    return result


class DiceBox():
  """
  A pile of prng streams.

  Streams are indexed by a kind and an id. The idea here is that each
  individual step will be used only once per id. The root seed is used to
  generate seeds for each individual kind, which are offset using the id as
  seeds.

  Separating the prng this way makes it less likely minor changes in one
  """

  def __init__(self, seed: int):
    if seed not in range(0, MAX_SEED):
      raise ValueError(f'Seed {seed:x} is not between 0 and {MAX_SEED:x}')
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
