from typing import Optional

import hashlib
import math
import numpy as np
import random
import re
import time

from .thing_random import ThingRandom

_MAX_SEED = 0x8000_0000

_STAGES_WITH_RNG = (
  # Any stage using random numbers must be listed here.
  # If new steps are added, append them to this list
  # to minimize disruption to existing caverns.
  'bubble',
  'weave',
  'conquest',
  'rough',
  'fine',
  'flood',
  'init',
  'enscribe',
)

class Seeder(object):

  def __init__(self, seed: int):
    stage_rng = np.random.default_rng(seed)
    self._seeds = {
      k: stage_rng.integers(0, _MAX_SEED)
      for k in _STAGES_WITH_RNG
    }
    self._current_stage = 'init'
    self._rng = {}

  def rng(self, stage: str, id: int) -> ThingRandom:
    # The seeder may only perform one stage at a time.
    # If this is a new stage, destroy the cache of RNG
    if stage != self._current_stage:
      if stage not in self._seeds:
        if stage in _STAGES_WITH_RNG:
          raise KeyError(
            f'{stage} has completed and can no longer generate numbers')
        else:
          raise KeyError(
            f'{stage} has no rng defined')
      del self._seeds[self._current_stage]
      self._current_stage = stage
      self._rng.clear()

    if id not in self._rng:
      # To get the seed for this specific RNG, just shift it by a fixed amount.
      # 1999 is an arbitrarily chosen constant.
      seed = (self._seeds[stage] + id * 1999) % _MAX_SEED
      self._rng[id] = ThingRandom(np.random.default_rng(seed))
    return self._rng[id]

  @staticmethod
  def coerce_seed(seed: Optional[str]) -> int:
    """Coerces the given seed into a number that is an acceptable seed."""
    # No seed: Use seconds since epoch
    if seed is None:
      return int(time.time()) % _MAX_SEED

    # Seed that looks like a hex number: use that as seed
    m = re.match(r'\A(0x)?(?P<seed>[0-9a-fA-F]{1,8})\Z', seed)
    if m:
      return int(m.group('seed'), 16)

    # Anything else: Take bits from the MD5 hash of the given phrase
    md5 = hashlib.md5()
    md5.update(seed.encode('utf-8'))
    return int(md5.hexdigest()[:8], 16) % _MAX_SEED