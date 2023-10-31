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
      for (x, y), layer, sequence
      in self.pearl
      if diorama.tiles.get((x, y)) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      crystals = self.expected_crystals
      
      for _ in range(crystals):
        x, y = self.rng.choice(t)
        existing = diorama.crystals.get((x, y), 0)
        if existing >= 3 and diorama.tiles.get((x, y)) != Tile.CRYSTAL_SEAM:
          diorama.tiles[x, y] = Tile.CRYSTAL_SEAM
          diorama.crystals[x, y] = existing - 3
        else:
          diorama.crystals[x, y] = existing + 1
    else:
      self.context.logger.log_warning(f'Nowhere to put crystals in {self.id}')
      diorama.crystals[self.pearl[0].pos] += self.expected_crystals