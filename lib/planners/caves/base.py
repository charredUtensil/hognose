import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile
from lib.utils.geometry import plot_line

class BaseCavePlanner(SomaticPlanner):

  def pearl_nucleus(self):
    r = self.pearl_radius
    def h():
      for bp in self.baseplates:
        ox = min(r, (bp.width  - 1) // 2)
        oy = min(r, (bp.height - 1) // 2)
        for x in range(bp.left + ox, bp.right - ox):
          for y in range(bp.top + oy, bp.bottom - oy):
            yield x, y
    return sorted(set(itertools.chain(self.walk_stream(), h())))

  def fine(self, diorama):
    t = tuple(
      (x, y)
      for (x, y), u
      in self._pearl
      if diorama.tiles.get((x, y)) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      for _ in range(self.expected_crystals):
        diorama.crystals[self.rng.choice(t)] += 1
    else:
      self.context.logger.log_warning(f'Nowhere to put crystals in {self.id}')
      diorama.crystals[tuple(math.floor(v) for v in self.baseplates[0].center)] += self.expected_crystals