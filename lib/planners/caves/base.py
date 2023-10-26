import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile
from lib.utils.geometry import plot_line

class BaseCavePlanner(SomaticPlanner):

  def rough(self, tiles):
    for (x, y), u in self.walk_blob():
      if tiles.get((x, y)) not in (Tile.WATER, Tile.LAVA):
        for t, tile in self.onion.stops():
          if u < t:
            tiles[x, y] = tile
            break

  def fine(self, diorama):
    t = tuple(
      (x, y)
      for (x, y), u
      in self.walk_blob()
      if diorama.tiles.get((x, y)) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      for _ in range(self.expected_crystals):
        diorama.crystals[self.rng.choice(t)] += 1
    else:
      print(f'nowhere to put crystals in {self.id}!')
      diorama.crystals[tuple(math.floor(v) for v in self.baseplates[0].center)] += self.expected_crystals