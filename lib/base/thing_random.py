from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")

import hashlib
import math
import numpy as np
import random
import re
import time

class ThingRandom(object):
  """Produces pseudorandom numbers for a thing at a stage."""

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