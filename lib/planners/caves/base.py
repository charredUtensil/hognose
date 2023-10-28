import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile
from lib.utils.geometry import plot_line

class BaseCavePlanner(SomaticPlanner):

  def walk(self):
    r = min(min(bp.width, bp.height) for bp in self.baseplates) // 2
    def h():
      for bp in self.baseplates:
        ox = min(r, (bp.width  - 1) // 2)
        oy = min(r, (bp.height - 1) // 2)
        for x in range(bp.left + ox, bp.right - ox):
          for y in range(bp.top + oy, bp.bottom - oy):
            yield x, y
    core = sorted(set(itertools.chain(self.walk_stream(), h())))
    self._pearl = tuple(self.walk_pearl(sorted(core), r + 1))
    return self._pearl

  def rough(self, tiles):
    self.walk()
    nacre = self.oyster.create(self._pearl[-1][-1])
    for (x, y), layer in self._pearl:
      tiles[x, y] = nacre.layers[layer]._place

  def fine(self, diorama):
    t = tuple(
      (x, y)
      for (x, y), u
      in self.walk()
      if diorama.tiles.get((x, y)) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      for _ in range(self.expected_crystals):
        diorama.crystals[self.rng.choice(t)] += 1
    else:
      print(f'nowhere to put crystals in {self.id}!')
      diorama.crystals[tuple(math.floor(v) for v in self.baseplates[0].center)] += self.expected_crystals