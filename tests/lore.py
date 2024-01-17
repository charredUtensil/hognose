from typing import FrozenSet

from lib.lore.conclusions import SUCCESS, FAILURE
from lib.lore.orders import ORDERS
from lib.lore.phrases import PhraseGraph
from lib.lore.premises import PREMISES

import unittest

STATE_COMBOS = (
  ('start',),
  (None, 'commend', 'console'),
  (None, 'flooded_water', 'flooded_lava'),
  ('collect_resources', 'lost_miners_one', 'lost_miners_together', 'lost_miners_apart'),
  (None, 'collect_resources'),
  (None, 'spawn_has_erosion'),
  (None, 'has_monsters'),
  (None, 'spawn_is_ruin', 'spawn_is_hq', 'find_hq'),
  (None, 'treasure_one', 'treasure_many'),
  ('end',),
)

def _all_possible_states(pg: PhraseGraph, states: FrozenSet[str], i: int):
  if i >= len(STATE_COMBOS):
    yield states
  else:
    for s in STATE_COMBOS[i]:
      if s and s in pg._states:
        yield from _all_possible_states(pg, states | frozenset((s,)), i + 1)
      else:
        yield from _all_possible_states(pg, states, i + 1)

class TestLore(unittest.TestCase):

  def _test_comprehensive(self, pg):
    for states in _all_possible_states(pg, frozenset(), 0):
      self.assertTrue(
        states in pg._phrases[0]._tagged_states,
        f'Phrase graph has no value for {repr(states)}')

  def test_comprehensive_premises(self):
    self._test_comprehensive(PREMISES)

  def test_comprehensive_orders(self):
    self._test_comprehensive(ORDERS)

  def test_comprehensive_success(self):
    self._test_comprehensive(SUCCESS)

  def test_comprehensive_failure(self):
    self._test_comprehensive(FAILURE)