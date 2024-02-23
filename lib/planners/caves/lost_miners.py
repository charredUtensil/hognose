from typing import Tuple

import math

from .base import BaseCavePlanner
from lib.base import Biome
from lib.holistics import Adjurator
from lib.planners.base import Oyster, Layer
from lib.plastic import Position, Script, ScriptFragment, Tile

class LostMinersCavePlanner(BaseCavePlanner):

  def __init__(self, stem, oyster):
    super().__init__(stem, oyster)
    self._miners = []

  @property
  def inspect_color(self):
    return (0xff, 0xff, 0x00)

  def _get_monster_spawner(self):
    return None

  @property
  def miners_tile(self) -> Tuple[int, int]:
    return next(self.pearl.nucleus).pos

  def fine_place_entities(self, diorama):
    rng = self.rng['fine.place_entities']
    pos = self.miners_tile
    diorama.tiles[pos] = Tile.FLOOR
    miners_count = math.floor(rng.beta(a = 1, b = 2, min = 1, max = 5))
    for _ in range(miners_count):
      self._miners.append(diorama.miner(Position.randomly_in_tile(rng, pos)))
  
  def adjure(self, adjurator):
    adjurator.find_miners(self.miners_tile, len(self._miners))

  def script(self, diorama, lore):
    prefix = f'foundMiners_p{self.id}_'
    x, y = self.miners_tile
    miners_found_count = len(self._miners)
    msg = Script.escape_string(
        lore.event_found_lost_miners(self.rng, miners_found_count))
    global_count = Adjurator.VAR_LOST_MINERS_COUNT
    on_found_all = Adjurator.ON_FOUND_ALL_LOST_MINERS
    def h():
      yield '# Objective: Find lost miners'
      yield f'string {prefix}discoverMessage="{msg}"'
      yield f'if(change:y@{y:d},x@{x:d})[{prefix}onDiscover]'
      yield f'{prefix}onDiscover::;'
      yield f'pan:y@{y:d},x@{x:d};'
      yield f'{global_count}={global_count}-{miners_found_count};'
      yield f'(({global_count}>0))[{prefix}incomplete][{on_found_all}];'
      yield ''
      yield f'{prefix}incomplete::;'
      yield f'msg:{prefix}discoverMessage;'
      yield ''
    return super().script(diorama, lore) + ScriptFragment(h())

def bids(stem, conquest):
  if stem.fluid_type is None and conquest.remaining <= 3:
    # The L.M.S. Explorer's teleporters just seem to be real lousy in ice
    # caverns for some reason.
    multiplier = {
      Biome.ROCK: 1.0,
      Biome.ICE : 1.4,
      Biome.LAVA: 0.7,
    }[stem.context.biome]
    yield (multiplier, lambda: LostMinersCavePlanner(stem, Oysters.DEFAULT))

class Oysters:
  DEFAULT = (
    Oyster('Default')
      .layer(Layer.ALWAYS_FLOOR, width=2, shrink=1, grow=2)
      .layer(Layer.ALWAYS_LOOSE_ROCK, grow=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )