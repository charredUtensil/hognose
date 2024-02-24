from typing import Iterable, Optional, Tuple

import math

from lib.planners.caves.base import BaseCavePlanner
from lib.holistics import Adjurator
from lib.planners.base import Oyster, Layer
from lib.plastic import (
    Building, Facing, Position, Script, ScriptFragment, Tile)
from lib.utils.geometry import plot_line


class EstablishedHQCavePlanner(BaseCavePlanner):

  def __init__(self, stem, oyster, is_spawn, has_tool_store, is_ruin):
    super().__init__(stem, oyster)
    self.is_spawn = is_spawn
    self.has_tool_store = has_tool_store
    self.is_ruin = is_ruin
    self._discover_tile: Optional[Tuple[int, int]] = None

  def _get_expected_crystals(self):
    # pylint: disable=attribute-defined-outside-init
    self.expected_wall_crystals = super()._get_expected_crystals()
    self.building_templates = tuple(self._get_building_templates())
    return (self.expected_wall_crystals + sum(
        bt.crystals
        for bt, _, ir
        in self.building_templates
        if not ir))

  def _get_monster_spawner(self):
    spawner = super()._get_monster_spawner()
    spawner.min_initial_cooldown = 30
    spawner.max_initial_cooldown = 120
    return spawner

  @property
  def inspect_color(self):
    return (0x00, 0xff, 0xff)

  def fine(self, diorama):
    super().fine(diorama)
    self.fine_rubble(diorama)
    for info in self.pearl.inner:
      if (not diorama.tiles.get(info.pos, Tile.SOLID_ROCK).is_wall
          and info.pos not in diorama.discovered):
        self._discover_tile = info.pos

  def fine_crystals(self, diorama):
    self.place_crystals(diorama, self.expected_wall_crystals)

  def fine_recharge_seam(self, diorama):
    self.place_recharge_seam(diorama)

  def fine_landslides(self, diorama):
    if self.is_ruin:
      freq = (
        3 * self.context.cave_landslide_freq
        * sum(math.sqrt(bp.area) for bp in self.baseplates))
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
    # Buildings in the cave, whether they actually exist or are just rubble.
    buildings = []
    # Shuffle each layer of the pearl.

    def pq():
      q = []
      layer = 1
      for pt in self.pearl.inner:
        if pt.layer < 2:
          continue
        if pt.layer > layer:
          yield from rng.shuffle(q)
          q.clear()
          layer = pt.layer
        q.append(pt)
      yield from rng.shuffle(q)
    # Iterate through queue pf possible positions, roughly from inside out, and
    # queue of building templates in a predetermined order of importance.
    for pt in pq():
      if not template_queue:
        break
      type, level, is_rubble = template_queue[0]
      building = self._make_building(
          diorama, type, pt, level)
      if building:
        template_queue.pop(0)
        buildings.append(building)
        if not is_rubble:
          diorama.buildings.append(building)
        for x, y in building.foundation_tiles:
          diorama.tiles[x, y] = (
              Tile.LANDSLIDE_RUBBLE_4 if is_rubble else Tile.FOUNDATION)
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
          diorama.tiles[x, y] = (
              Tile.LANDSLIDE_RUBBLE_4
              if self.is_ruin and rng.chance(0.55)
              else Tile.POWER_PATH)

  def fine_rubble(self, diorama):
    if not self.is_ruin:
      return
    rng = self.rng['place_buildings']
    for pt in self._pearl.inner:
      if diorama.tiles.get(pt.pos, Tile.SOLID_ROCK) == Tile.FLOOR:
        diorama.tiles[pt.pos] = rng.beta_choice(a=1, b=3, choices=(
            Tile.FLOOR,
            Tile.LANDSLIDE_RUBBLE_1,
            Tile.LANDSLIDE_RUBBLE_2,
            Tile.LANDSLIDE_RUBBLE_3,
            Tile.LANDSLIDE_RUBBLE_4))

  def _get_building_templates(
      self) -> Iterable[Tuple[Building.Type, int, bool]]:
    rng = self.rng['conquest.expected_crystals']
    crystals = rng.beta_int(a=1, b=1.75, min=3, max=10)
    if self.has_tool_store:
      yield (Building.Type.TOOL_STORE, 2, False)
    elif self.is_ruin:
      yield (Building.Type.TOOL_STORE, 1, True)

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
      templates.extend(
          (type, level, True if i >= t1_count else is_ruin)
          for i, (type, level, is_ruin) in enumerate(rng.shuffle(t1)))
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

  def _make_building(
      self, diorama, type, pt, level) -> Optional[Building]:
    for facing, ox, oy in (
        (Facing.NORTH, 0, -1),
        (Facing.EAST, 1, 0),
        (Facing.SOUTH, 0, 1),
        (Facing.WEST, -1, 0)):
      x, y = pt.pos
      if (x + ox, y + oy) in self.pearl:
        pt2 = self.pearl[x + ox, y + oy]
        if pt2.layer < pt.layer:
          b = Building.at_tile(type, pt.pos, facing, level)
          if all(diorama.tiles.get((x, y)) == Tile.FLOOR
                 for x, y in b.foundation_tiles):
            return b
    return None

  def adjure(self, adjurator):
    if not self.is_spawn:
      adjurator.find_hq(self._discover_tile, 'Find the lost Rock Raider HQ')

  def script(self, diorama, lore):
    if self.is_spawn:
      return None
    prefix = f'foundHq_p{self.id}_'
    x, y = self._discover_tile
    bp = max(self.baseplates, key=lambda b: b.pearl_radius)
    cx, cy = bp.center
    msg = Script.escape_string(lore.event_found_hq)

    def h():
      yield '# Objective: Find the lost Rock Raider HQ'
      yield f'string {prefix}discoverMessage="{msg}"'
      yield f'if(change:y@{y:d},x@{x:d})[{prefix}onDiscover]'
      yield f'{prefix}onDiscover::;'
      yield f'msg:{prefix}discoverMessage;'
      yield f'pan:y@{math.floor(cy):d},x@{math.floor(cx):d};'
      yield 'wait:1;'
      yield f'{Adjurator.VAR_FOUND_HQ}=1;'
      yield ''
    return super().script(diorama, lore) + ScriptFragment(h())


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
  del conquest
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
