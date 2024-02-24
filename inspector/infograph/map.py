import math

from inspector.canvas import (
    Canvas, Circle, Label, LabelIfFits, Line, RadialLabel, Rect, v)
from inspector.infograph.common import (
    FONT_TINY, Z_BOUNDS, Z_TILES, Z_ENTITIES, Z_CRYSTALS, Z_ORE, Z_HAZARDS)
from lib.plastic import Diorama, Entity, Tile

BUILDING_COLOR = (0xff, 0xff, 0x00)
BUILDING_LABEL_COLOR = (0x44, 0x44, 0x00)
CREATURE_COLOR = (0xff, 0x00, 0x00)
CRYSTAL_COLOR = Tile.CRYSTAL_SEAM.inspect_color
EROSION_COLOR = Tile.LAVA.inspect_color
LANDSLIDE_COLOR = (0xff, 0x00, 0x00)
SHADOW_COLOR = (0x00, 0x00, 0x00)
MINER_COLOR = (0xff, 0xff, 0x00)
ORE_COLOR = Tile.ORE_SEAM.inspect_color

BUILDING_LABEL_RADIUS = 10


def _push_resource(canvas, count, color, origin):
  if count > 9:
    canvas.push(RadialLabel(
        font=FONT_TINY,
        text=f'{count:d}',
        fg_color=color,
        bg_color=(0, 0, 0),
        origin=origin))
  elif count > 4:
    canvas.push(Label(
        font=FONT_TINY,
        text=f'{count:d}',
        color=color,
        origin=origin,
        shadow_color=(0, 0, 0),
        shadow_offset=v.a(1)))
  elif count > 0:
    canvas.push(Circle(
        color=color,
        origin=origin,
        radius=count / 4,
        thickness=v.a(1)))


def _push_resources(canvas: Canvas, diorama: Diorama):
  oc = Canvas()
  ec = Canvas()
  for (x, y) in set(diorama.tiles) | set(diorama.ore) | set(diorama.crystals):
    ore = (
        diorama.ore.get((x, y), 0)
        + diorama.tiles.get((x, y), Tile.SOLID_ROCK).ore_yield
        - 4)
    if ore > 0:
      _push_resource(oc, ore, ORE_COLOR, (x + 0.25, y + 0.25))
    crystals = (
        diorama.crystals.get((x, y), 0)
        + diorama.tiles.get((x, y), Tile.SOLID_ROCK).crystal_yield)
    if crystals > 0:
      _push_resource(ec, crystals, CRYSTAL_COLOR, (x + 0.75, y + 0.75))
  canvas.push(oc.freeze(), Z_ORE)
  canvas.push(ec.freeze(), Z_CRYSTALS)


def _push_hazards(canvas: Canvas, diorama: Diorama):
  pc = Canvas()
  lc = Canvas()
  for (x, y), event in diorama.erosions.items():
    pc.push(Line(
        color=EROSION_COLOR,
        start=(x + 0.5, y + 0.25),
        end=(x + 0.5, y + 0.75)))
    pc.push(Line(
        color=EROSION_COLOR,
        start=(x + 0.25, y + 0.5),
        end=(x + 0.75, y + 0.5)))
    lc.push(LabelIfFits(
        font=FONT_TINY,
        text=str(event),
        color=EROSION_COLOR,
        rect=(x, y, 1, 0.5),
        shadow_color=SHADOW_COLOR,
        shadow_offset=v.a(1)))
  for (x, y), event in diorama.landslides.items():
    pc.push(Line(
        color=LANDSLIDE_COLOR,
        start=(x + 0.25, y + 0.25),
        end=(x + 0.75, y + 0.75)))
    pc.push(Line(
        color=LANDSLIDE_COLOR,
        start=(x + 0.25, y + 0.75),
        end=(x + 0.75, y + 0.25)))
    lc.push(LabelIfFits(
        font=FONT_TINY,
        text=str(event),
        color=LANDSLIDE_COLOR,
        rect=(x, y + 0.5, 1, 0.5),
        shadow_color=SHADOW_COLOR,
        shadow_offset=v.a(1)))
  canvas.push(pc.freeze(), Z_HAZARDS)
  canvas.push(lc.freeze(), Z_HAZARDS)


def _entity_line(entity: Entity, color, length, thickness) -> Line:
  theta = entity.theta
  return Line(
      color=color,
      start=(entity.x, entity.y),
      end=(
          entity.x + math.cos(theta) * length,
          entity.y + math.sin(theta) * length),
      thickness=thickness)


def _push_entities(canvas: Canvas, diorama: Diorama):
  pc = Canvas()
  for building in diorama.buildings:
    rect = (
        v.x(building.x - 0.5) + v.a(1),
        v.y(building.y - 0.5) + v.a(1),
        v.s(1) - v.a(2),
        v.s(1) - v.a(2))
    pc.push(Rect(
        color=BUILDING_COLOR,
        rect=rect))
    pc.push(_entity_line(building, BUILDING_COLOR, 0.75, v.s(0.5)))
    pc.push(LabelIfFits(
        font=FONT_TINY,
        text=building.type.inspect_abbrev,
        color=BUILDING_LABEL_COLOR,
        rect=rect))
  canvas.push(pc.freeze(), Z_ENTITIES)
  pc.clear()
  for creature in diorama.creatures:
    pc.push(Circle(
        color=CREATURE_COLOR,
        origin=(creature.x, creature.y),
        radius=v.s(0.25)))
    pc.push(_entity_line(creature, CREATURE_COLOR, 1, v.a(1)))
  canvas.push(pc.freeze(), Z_ENTITIES)
  pc.clear()
  for miner in diorama.miners:
    pc.push(Circle(
        color=MINER_COLOR,
        origin=(miner.x, miner.y),
        radius=v.s(0.25)))
    pc.push(_entity_line(miner, MINER_COLOR, 1, v.a(1)))
  canvas.push(pc.freeze(), Z_ENTITIES)


def push_map(canvas: Canvas, diorama: Diorama):
  pc = Canvas()
  for (x, y), tile in diorama.tiles.items():
    color = tile.inspect_color
    pc.push(Rect(color, (x, y, 1, 1)))
  canvas.push(pc.freeze(), Z_TILES)
  pc.clear()
  if diorama.bounds:
    canvas.push(Rect(
        color=Tile.SOLID_ROCK.inspect_color,
        rect=diorama.bounds), Z_BOUNDS)
  _push_resources(canvas, diorama)
  _push_hazards(canvas, diorama)
  _push_entities(canvas, diorama)
