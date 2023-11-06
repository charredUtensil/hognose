import collections
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
    self.place_crystals(diorama)

  def place_crystals(self, diorama):
    t = tuple(
      pearl_info.pos
      for pearl_info
      in self.pearl
      if diorama.tiles.get(pearl_info.pos) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
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
      def placements():
        for pearl_info in self.walk_pearl(
            (p.pos for p in self.pearl),
            max_layers = 2,
            include_nucleus = False,
            baroqueness = 0):
          x, y = pearl_info.pos
          if diorama.tiles.get((x, y), Tile.SOLID_ROCK) == Tile.SOLID_ROCK:
            neighbor_count = collections.Counter()
            for (ox, oy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
              neighbor_count[diorama.tiles.get((x + ox, y + oy), Tile.SOLID_ROCK)] += 1
            if any(n.passable_by_miner for n in neighbor_count):
              yield neighbor_count[Tile.SOLID_ROCK], (x, y)
      _, (x, y) = max(placements())
      crystals = self.expected_crystals
      if crystals >= 4:
        diorama.tiles[x, y] = Tile.CRYSTAL_SEAM
        crystals -= 4
      diorama.crystals[x, y] += crystals
