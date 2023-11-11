import collections
import itertools
import math

from lib.planners.base import SomaticPlanner
from lib.plastic import Diorama, Tile
from lib.utils.geometry import plot_line

class BaseCavePlanner(SomaticPlanner):

  @property
  def baroqueness(self) -> float:
    return self.context.cave_baroqueness

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
    self.fine_recharge_seam(diorama)
    self.fine_buildings(diorama)
    self.fine_crystals(diorama)
    self.fine_landslides(diorama)
    self.fine_erosion(diorama)

  def fine_recharge_seam(self, diorama: Diorama):
    if self.rng['fine.place_recharge_seam'].random() < self.context.recharge_seam_chance:
      self.place_recharge_seam(diorama)

  def fine_buildings(self, diorama: Diorama):
    pass

  def fine_crystals(self, diorama: Diorama):
    self.place_crystals(diorama, self.expected_crystals)

  def fine_landslides(self, diorama: Diorama):
    if self.rng['fine.place_landslides'].random() < self.context.cave_landslide_chance:
      freq = self.context.cave_landslide_freq * sum(math.sqrt(bp.area()) for bp in self.baseplates)
      self.place_landslides(diorama, freq)

  def place_crystals(self, diorama: Diorama, count: int):
    rng = self.rng['fine.place_crystals']
    t = tuple(
      pearl_info.pos
      for pearl_info
      in self.pearl
      if diorama.tiles.get(pearl_info.pos) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      for _ in range(count):
        x, y = rng.choice(t)
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
          tile = diorama.tiles.get((x, y), Tile.SOLID_ROCK)
          if tile == Tile.SOLID_ROCK:
            neighbor_count = collections.Counter()
            for (ox, oy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
              neighbor_count[
                  diorama.tiles.get((x + ox, y + oy), Tile.SOLID_ROCK)] += 1
            if any(
                n not in (Tile.SOLID_ROCK, Tile.RECHARGE_SEAM)
                for n in neighbor_count):
              yield neighbor_count[Tile.SOLID_ROCK], (x, y)
          elif tile in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK):
            yield 4, (x, y)
      try:
        _, (x, y) = max(placements())
        crystals = count
        if crystals >= 4:
          diorama.tiles[x, y] = Tile.CRYSTAL_SEAM
          crystals -= 4
        elif diorama.tiles.get((x, y), Tile.SOLID_ROCK) == Tile.SOLID_ROCK:
          diorama.tiles[x, y] = Tile.LOOSE_ROCK
        diorama.crystals[x, y] += crystals
      except ValueError:
        self.context.logger.log_warning(
            f'Failed to place crystals in #{self.id}')

  def place_recharge_seam(self, diorama):
    def placements():
      for pearl_info in self.walk_pearl(
          (p.pos for p in self.pearl),
          max_layers = 4,
          include_nucleus = False,
          baroqueness = 0):
        x, y = pearl_info.pos
        if diorama.tiles.get((x, y), Tile.SOLID_ROCK) == Tile.SOLID_ROCK:
          neighbor_count = collections.Counter()
          for (ox, oy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            neighbor_count[
                diorama.tiles.get((x + ox, y + oy),
                Tile.SOLID_ROCK)] += 1
          if any(n.passable_by_miner for n in neighbor_count):
            value = neighbor_count[Tile.SOLID_ROCK] * 5
            for ox in (-1, 1):
              for oy in (-1, 1):
                if diorama.tiles.get((), Tile.SOLID_ROCK) == Tile.SOLID_ROCK:
                  value += 1
            yield value, (x, y)
    try:
      _, (x, y) = max(placements())
      diorama.tiles[x, y] = Tile.RECHARGE_SEAM
    except ValueError:
      self.context.logger.log_warning(
          f'Failed to place recharge seam in #{self.id}')