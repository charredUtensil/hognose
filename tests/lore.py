from parameterized import parameterized
from typing import FrozenSet

from lib.lore.conclusions import SUCCESS, FAILURE
from lib.lore.events import FOUND_HOARD, FOUND_HQ
from lib.lore.orders import ORDERS
from lib.lore.phrases import PhraseGraph
from lib.lore.premises import PREMISES

import unittest

STATE_COMBOS = (
  ('start',),
  (None, 'commend', 'console'),
  (None, 'flooded_water', 'flooded_lava'),
  (
      'collect_resources',
      'lost_miners_one',
      'lost_miners_together',
      'lost_miners_apart'
  ),
  (None, 'collect_resources'),
  (None, 'spawn_has_erosion'),
  (None, 'has_monsters'),
  (None, 'spawn_is_ruin', 'spawn_is_hq', 'find_hq'),
  (None, 'treasure_one', 'treasure_many'),
  ('end',),
)

def _all_possible_states(pg: PhraseGraph) -> FrozenSet[FrozenSet[str]]:
  result: FrozenSet[FrozenSet[str]] = frozenset((frozenset(),))
  for choices in STATE_COMBOS:
    append = frozenset(
        (frozenset((s,)) if s and s in pg._states else frozenset())
        for s in choices)
    def h():
      for r in result:
        for a in append:
          yield r | a
    result = frozenset(h())
  return result

class TestLore(unittest.TestCase):
  
  @parameterized.expand((
      ('premises', PREMISES),
      ('orders', ORDERS),
      ('success', SUCCESS),
      ('failure', FAILURE),
      ('foundHoard', FOUND_HOARD),
      ('foundHq', FOUND_HQ),
  ))
  def test_loreIsComprehensive(self, _, pg):
    for states in _all_possible_states(pg):
      self.assertTrue(
        states in pg._phrases[0]._tagged_states,
        f'Phrase graph has no value for {repr(states)}')