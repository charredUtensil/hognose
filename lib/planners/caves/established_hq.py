from typing import Iterable, Optional, Tuple

import math

from .base import BaseCavePlanner
from lib.base import Biome
from lib.planners.base import Oyster, Layer
from lib.plastic import Building, Facing, Position, Tile
from lib.utils.geometry import plot_line

class EstablishedHQCavePlanner(BaseCavePlanner):

  def __init__(self, stem, oyster, is_spawn, has_tool_store, is_ruin):
    super().__init__(stem, oyster)
    self.is_spawn = is_spawn
    self.has_tool_store = has_tool_store
    self.is_ruin = is_ruin

  def _get_expected_crystals(self):
    self.expected_wall_crystals = super()._get_expected_crystals()
    self.building_templates = tuple(self._get_building_templates())
    return (self.expected_wall_crystals + sum(
        bt.crystals
        for bt, _, ir
        in self.building_templates
        if not ir))
    
  @property
  def inspect_color(self):
    return (0x00, 0xff, 0xff)
  
  def fine_crystals(self, diorama):
    self.place_crystals(diorama, self.expected_wall_crystals)

  def fine_recharge_seam(self, diorama):
    self.place_recharge_seam(diorama)

  def fine_landslides(self, diorama):
    if self.is_ruin:
      freq = (
        3 * self.context.cave_landslide_freq
        * sum(math.sqrt(bp.area()) for bp in self.baseplates))
      self.place_landslides(diorama, freq)
    else:
      super().fine_landslides(diorama)
      return

  def fine_buildings(self, diorama):
    rng = self.rng['place_buildings']
    bp = max(self.baseplates, key=lambda b: b.pearl_radius)

    assert self.building_templates is not None
    template_queue = []
    template_queue.extend(self.building_templates)
    buildings = []
    for pt in self.pearl.inner:
      if pt.layer < 2:
        continue
      if template_queue:
        type, level, is_rubble = template_queue[0]
        building = self._make_building(
            diorama,
            rng,
            type,
            pt,
            level)
        if building:
          template_queue.pop(0)
          buildings.append(building)
          if not is_rubble:
            diorama.buildings.append(building)
          for x, y in building.foundation_tiles:
            diorama.tiles[x, y] = (
                Tile.RUBBLE_4 if is_rubble else Tile.FOUNDATION)
          continue
    if template_queue:
      self.context.logger.log_warning(
          f'failed to place remaining {len(template_queue)} buildings')
    if self.is_spawn:
      diorama.open_cave_flags.add(buildings[0].foundation_tiles[0])
      x, y = bp.center
      diorama.camera_position = Position(
          (x, y, 0), (math.pi / 4, math.pi * 0.75, 0))
    for building in buildings:
      for x, y in plot_line(building.foundation_tiles[-1], bp.center, True):
        if diorama.tiles.get((x, y)) == Tile.FLOOR:
          if self.is_ruin and rng.chance(0.55):
            diorama.tiles[x, y] = Tile.RUBBLE_4
          else:
            diorama.tiles[x, y] = Tile.POWER_PATH

  def _get_building_templates(self) -> Iterable[Tuple[Building.Type, int]]:
    rng = self.rng['conquest.expected_crystals']
    crystals = rng.beta_int(a = 1, b = 1.75, min = 3, max = 10)
    if self.has_tool_store:
      yield (Building.Type.TOOL_STORE, 2, False)

    t1 = (
        (Building.Type.TELEPORT_PAD, 2, False),
        (Building.Type.POWER_STATION, 2, False),
        (Building.Type.SUPPORT_STATION, 1, False),
    )
    t2 = (
        (Building.Type.UPGRADE_STATION, 1, False),
        (Building.Type.GEOLOGICAL_CENTER, 1, False),
        (Building.Type.MINING_LASER, 1, False),
    )
    t3 = (
        (Building.Type.MINING_LASER, 1, False),
        (Building.Type.MINING_LASER, 1, False),
    )
    templates = []
    if self.is_ruin:
      t1_count = rng.uniform_int(1, len(t1))
      t1s = rng.shuffle(t1)
      templates.extend(t1s[:t1_count])
      templates.extend(
          (a, b, True)
          for (a, b, _)
          in t1s[t1_count:])
    else:
      templates.extend(rng.shuffle(t1))
    templates.extend(rng.shuffle(t2))
    templates.extend(t3)
    for type, level, is_rubble in templates:
      if crystals >= type.crystals:
        yield type, level, is_rubble
        if not is_rubble:
          crystals -= type.crystals
      elif self.is_ruin and rng.chance(0.40):
        yield type, level, True
      

  def _make_building(self, diorama, rng, type, pt, level) -> Optional[Building]:
    for facing, ox, oy in (
        (Facing.NORTH,  0, -1),
        (Facing.EAST,   1,  0),
        (Facing.SOUTH,  0,  1),
        (Facing.WEST,  -1,  0)):
      x, y = pt.pos
      if (x + ox, y + oy) in self.pearl:
        pt2 = self.pearl[x + ox, y + oy]
        if pt2.layer < pt.layer:
          b = Building.at_tile(type, pt.pos, facing, level)
          if all(diorama.tiles.get((x, y)) == Tile.FLOOR
              for x, y in b.foundation_tiles):
            return b
    return None

def bids(stem, conquest):
  if (stem.fluid_type is None
      and stem.pearl_radius > 5
      and stem.hops_to_spawn <= 4
      and not any(
          isinstance(p, EstablishedHQCavePlanner)
          for p in conquest.planners)):
    yield (1, lambda: EstablishedHQCavePlanner(
        stem, Oysters.DEFAULT, False, False, is_ruin=False))

def spawn_bids(stem, conquest):
  if stem.fluid_type is None and stem.pearl_radius > 5:
    yield (0.25, lambda: EstablishedHQCavePlanner(
        stem, Oysters.DEFAULT, True, True, is_ruin=False))
    yield (0.75, lambda: EstablishedHQCavePlanner(
        stem, Oysters.DEFAULT, True, True, is_ruin=True))

class Oysters:
  DEFAULT = (
    Oyster('Default')
      .layer(Layer.ALWAYS_FLOOR, grow=2)
      .layer(Layer.FLOOR, grow=2)
      .layer(Layer.DIRT, width=0, grow=0.5)
      .layer(Layer.DIRT_OR_LOOSE_ROCK, grow=0.25)
      .layer(Layer.HARD_ROCK, grow=0.25)
  )