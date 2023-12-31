from typing import Tuple

import itertools
import math

from .base import BaseCavePlanner
from .monster_spawners import MonsterSpawner, RetriggerMode
from lib.base import Biome
from lib.planners.base import Oyster, Layer
from lib.plastic import Creature, Position, ResourceObjective, Tile

class TreasureCavePlanner(BaseCavePlanner):

  def _get_expected_crystals(self):
    return math.floor(super()._get_expected_crystals()
       * self.rng['conquest.expected_crystals'].beta(min = 1, max = 4))
  
  @property
  def objectives(self):
    crystals = self.expected_crystals
    crystals -= (crystals % 5)
    if crystals >= 15:
      return [ResourceObjective(crystals=crystals)]
    else:
      return []

class HoardCavePlanner(TreasureCavePlanner):

  def _get_monster_spawner(self):
    creature_type = Creature.Type.monster_for_biome(self.context.biome)
    spawner = MonsterSpawner.normal(
        self,
        creature_type,
        self._stem.monster_spawn_rate * 3.5,
        self._stem.monster_wave_size * 1.5)
    spawner.retrigger_mode = RetriggerMode.HOARD
    return spawner

  def _monster_placements(self, diorama):
    accepted_tiles = set((Tile.FLOOR,))
    if self.context.biome == Biome.ICE:
      accepted_tiles.add(Tile.WATER)
    if self.context.biome == Biome.LAVA:
      accepted_tiles.add(Tile.LAVA)
    
    layer = 0
    r = []
    for info in self.pearl.inner:
      if info.layer > layer + 1:
        break
      if diorama.tiles[info.pos] in accepted_tiles:
        if info.layer > layer:
          r.clear()
          layer = info.layer
        r.append(info.pos)
    return r

  def fine_crystals(self, diorama):
    self.place_crystals(diorama, math.floor(self.expected_crystals * 0.2))
    places = tuple(pt.pos for pt in self.pearl.nucleus)
    for x, y in itertools.islice(
        itertools.cycle(places), math.ceil(self.expected_crystals * 0.8)):
      diorama.crystals[x, y] += 1
  
  def fine_place_entities(self, diorama):
    if self.context.has_monsters:
      rng = self.rng['fine.place_entities']
      monster_type = Creature.Type.monster_for_biome(self.context.biome)
      monster_count = rng.beta_int(a = 1.5, b = 5, min = 0, max = 6)
      center = self.center
      tiles = tuple(self._monster_placements(diorama))
      for _ in range(monster_count):
        diorama.creature(
          monster_type,
          Position.randomly_in_tile(
              rng,
              rng.uniform_choice(tiles),
              facing=center),
          sleep=True)

class NougatCavePlanner(TreasureCavePlanner):

  def _get_monster_spawner(self):
    creature_type = Creature.Type.monster_for_biome(self.context.biome)
    spawner = MonsterSpawner.normal(
        self,
        creature_type,
        self._stem.monster_spawn_rate * 2,
        self._stem.monster_wave_size * 1.5)
    spawner.spawn_immediately_when_ready = True
    return spawner

  def fine_crystals(self, diorama):
    t = tuple(
      pt.pos
      for pt
      in self.pearl.inner
      if diorama.tiles.get(pt.pos) in (Tile.DIRT, Tile.LOOSE_ROCK, Tile.HARD_ROCK))
    if t:
      rng = self.rng['fine.place_crystals']
      count = math.ceil(self.expected_crystals * 0.8)
      while count > 0:
        x, y = rng.beta_choice(t, a = 0.7, b = 1.3)
        if count >= 4 and diorama.tiles.get((x, y)) != Tile.CRYSTAL_SEAM:
          diorama.tiles[x, y] = Tile.CRYSTAL_SEAM
          count -= 4
        else:
          diorama.crystals[x, y] += 1
          count -= 1
      self.place_crystals(diorama, math.floor(self.expected_crystals * 0.2))
    else:
      super().fine_crystals(diorama)

def bids(stem, conquest):
  if sum(1 for _ in conquest.intersecting(stem)) > 1:
    # Only put treasure caves at dead ends
    return
  pr = stem.pearl_radius
  if stem.fluid_type == Tile.WATER and pr > 3:
    yield (0.5, lambda: NougatCavePlanner(
        stem, Oysters.ISLAND_NOUGAT))
    if not any(p.fluid_type for p in conquest.intersecting(stem)):
      yield (0.5, lambda: HoardCavePlanner(
          stem, Oysters.PENINSULA_HOARD))
  elif stem.fluid_type == Tile.LAVA and pr > 3:
    yield (0.5, lambda: NougatCavePlanner(
        stem, Oysters.LAVA_ISLAND_NOUGAT))
    if not any(p.fluid_type for p in conquest.intersecting(stem)):
      yield (0.5, lambda: HoardCavePlanner(
          stem, Oysters.LAVA_PENINSULA_HOARD))
  elif len(stem.baseplates) > 1:
    yield (1, lambda: NougatCavePlanner(stem, Oysters.OPEN_NOUGAT))
  else:
    yield (0.5, lambda: HoardCavePlanner(stem, Oysters.OPEN_HOARD))
    yield (0.5, lambda: HoardCavePlanner(stem, Oysters.SEALED_HOARD))

class Oysters:
  OPEN_HOARD = (
    Oyster('Open Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  SEALED_HOARD = (
    Oyster('Sealed Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=1, grow=3)
      .layer(Layer.ALWAYS_LOOSE_ROCK)
      .layer(Layer.ALWAYS_HARD_ROCK, grow=0.5)
  )

  OPEN_NOUGAT = (
      Oyster('Open Nougat')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=1)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.5)
      .layer(Layer.LOOSE_ROCK, grow=2)
      .layer(Layer.FLOOR, width=2, shrink=1, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  ISLAND_NOUGAT = (
    Oyster('Island Nougat')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=1)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.5)
      .layer(Layer.ALWAYS_LOOSE_ROCK, grow=2)
      .layer(Layer.WATER, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  PENINSULA_HOARD = (
    Oyster('Peninsula Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=1)
      .layer(Layer.BRIDGE_ON_WATER, width=2, grow=3)
      .layer(Layer.LOOSE_ROCK, shrink=1)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  LAVA_ISLAND_NOUGAT = (
    Oyster('Lava Island Nougat')
      .layer(Layer.ALWAYS_SOLID_ROCK, width=0, grow=1)
      .layer(Layer.ALWAYS_HARD_ROCK, width=0, grow=0.5)
      .layer(Layer.ALWAYS_LOOSE_ROCK, grow=2)
      .layer(Layer.LAVA, width=2, grow=3)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )

  LAVA_PENINSULA_HOARD = (
    Oyster('Lava Peninsula Hoard')
      .layer(Layer.ALWAYS_FLOOR, width=2, grow=1)
      .layer(Layer.BRIDGE_ON_LAVA, width=2, grow=3)
      .layer(Layer.HARD_ROCK, grow=0.5)
  )