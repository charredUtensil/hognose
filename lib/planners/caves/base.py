from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
  from lib.lore import Lore

import abc
import collections
import functools
import itertools
import math

from .monster_spawners import MonsterSpawner
from lib.planners.base import SomaticPlanner
from lib.plastic import Creature, Diorama, Tile
from lib.utils.geometry import plot_line

class BaseCavePlanner(SomaticPlanner):

  @property
  def baroqueness(self) -> float:
    return self.context.cave_baroqueness

  @functools.cached_property
  def expected_ore(self) -> int:
    return self._get_expected_ore()

  def _get_expected_crystals(self):
    area = sum(bp.area for bp in self.baseplates)
    mean = math.sqrt(area) * self._stem.crystal_richness
    return self.rng['conquest.expected_crystals'].beta_int(
        a = 5, b = 2, min = 0, max = mean * 1.25)

  def _get_expected_ore(self):
    area = sum(bp.area for bp in self.baseplates)
    mean = math.sqrt(area) * self._stem.ore_richness
    return self.rng['expected_ore'].beta_int(
        a = 5, b = 2, min = 0, max = mean * 1.25)

  @functools.cached_property
  def monster_spawner(self) -> Optional[MonsterSpawner]:
    return self._get_monster_spawner() if self.context.has_monsters else None

  def _get_monster_spawner(self) -> Optional[MonsterSpawner]:
    creature_type = Creature.Type.monster_for_biome(self.context.biome)
    spawner = MonsterSpawner.normal(
        self,
        creature_type,
        self._stem.monster_spawn_rate,
        self._stem.monster_wave_size)
    return spawner

  def make_nucleus(self):
    def h():
      mpr = self.pearl_radius
      for bp in self.baseplates:
        pr = bp.pearl_radius
        ox = min(pr, (bp.width  - 1) // 2)
        oy = min(pr, (bp.height - 1) // 2)
        for x in range(bp.left + ox, bp.right - ox):
          for y in range(bp.top + oy, bp.bottom - oy):
            yield mpr - pr, (x, y)
      for a, b in itertools.pairwise(self.baseplates):
        pr = min(a.pearl_radius, b.pearl_radius)
        for x, y in plot_line(a.center, b.center, contiguous=True):
          yield mpr - pr, (x, y)
    layers = set()
    r = {}
    for ly, pos in h():
      r[pos] = min(ly, r.get(pos, ly))
      layers.add(ly)
    return {
        cly: sorted(pos for (pos, ly) in r.items() if ly == cly)
        for cly in sorted(layers)}

  def fine(self, diorama):
    self.fine_recharge_seam(diorama)
    self.fine_buildings(diorama)
    self.fine_crystals(diorama)
    self.fine_ore(diorama)
    self.fine_landslides(diorama)
    self.fine_erosion(diorama)
    self.fine_place_entities(diorama)

  def fine_recharge_seam(self, diorama: Diorama):
    if self.rng['fine.place_recharge_seam'].chance(self.context.recharge_seam_chance):
      self.place_recharge_seam(diorama)

  def fine_buildings(self, diorama: Diorama):
    pass

  def fine_crystals(self, diorama: Diorama):
    self.place_crystals(diorama, self.expected_crystals)

  def fine_ore(self, diorama: Diorama):
    self.place_ore(diorama, self.expected_ore)

  def fine_landslides(self, diorama: Diorama):
    if self.rng['fine.place_landslides'].chance(self.context.cave_landslide_chance):
      freq = self.context.cave_landslide_freq * sum(math.sqrt(bp.area) for bp in self.baseplates)
      self.place_landslides(diorama, freq)

  def fine_place_entities(self, diorama: Diorama):
    pass

  def script(self, diorama: Diorama, lore: 'Lore'):
    header = str(self)
    diorama.script.extend((
        f'# {"=" * len(header)}',
        f'# {header}',
        f'# {"=" * len(header)}'))
    self.script_place_monster_spawns(diorama)

  def script_place_monster_spawns(self, diorama: Diorama):
    monster_spawner = self.monster_spawner
    if monster_spawner:
      monster_spawner.place_script(diorama)

  def place_crystals(self, diorama: Diorama, count: int):
    self._place_resource(
        self.rng['fine.place_crystals'],
        Tile.CRYSTAL_SEAM,
        'crystals',
        diorama.tiles,
        diorama.crystals,
        count)

  def place_ore(self, diorama: Diorama, count: int):
    self._place_resource(
        self.rng['place_ore'],
        Tile.ORE_SEAM,
        'ore',
        diorama.tiles,
        diorama.ore,
        count)
    
  def _place_resource(
      self,
      rng,
      seam,
      resource_name,
      tiles,
      resource,
      count):
    t = tuple(
      pearl_info.pos
      for pearl_info
      in self.pearl.inner
      if tiles.get(pearl_info.pos) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      for _ in range(count):
        x, y = rng.uniform_choice(t)
        existing = resource.get((x, y), 0)
        if existing >= 3 and tiles.get((x, y)) != seam:
          tiles[x, y] = seam
          resource[x, y] = existing - 3
        else:
          resource[x, y] = existing + 1
    else:
      def placements():
        for pearl_info in self.pearl.outer:
          x, y = pearl_info.pos
          tile = tiles.get((x, y), Tile.SOLID_ROCK)
          if tile == Tile.SOLID_ROCK:
            neighbor_count = collections.Counter()
            for (ox, oy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
              neighbor_count[
                  tiles.get((x + ox, y + oy), Tile.SOLID_ROCK)] += 1
            if any(
                n not in (Tile.SOLID_ROCK, Tile.RECHARGE_SEAM)
                for n in neighbor_count):
              yield neighbor_count[Tile.SOLID_ROCK], (x, y)
          elif tile in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK):
            yield 4, (x, y)
      try:
        _, (x, y) = max(placements())
        remaining = count
        if remaining >= 4:
          tiles[x, y] = seam
          remaining -= 4
        elif tiles.get((x, y), Tile.SOLID_ROCK) == Tile.SOLID_ROCK:
          tiles[x, y] = Tile.LOOSE_ROCK
        resource[x, y] += remaining
      except ValueError:
        self.context.logger.log_warning(
            f'Failed to place {resource_name} in #{self.id}')

  def place_recharge_seam(self, diorama):
    def placements():
      for pearl_info in self.pearl.outer:
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