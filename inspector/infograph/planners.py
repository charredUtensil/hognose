import itertools

from inspector.canvas import Canvas, Circle, Color, Gravity, Label, Line, v
from inspector.infograph.common import FONT_TINY, Z_PLANNERS
from lib.planners import Planner, SomaticPlanner, StemPlanner
from lib.planners.caves.base import BaseCavePlanner
from lib.plastic import Tile

PLANNER_FLUID_COLORS = {
    None: Tile.FLOOR.inspect_color,
    Tile.WATER: Tile.WATER.inspect_color,
    Tile.LAVA: Tile.LAVA.inspect_color,
}
PLANNER_BORDER_COLOR = Tile.DIRT.inspect_color
PLANNER_ERODES_BORDER_COLOR = Tile.LAVA.inspect_color
PLANNER_TEXT_COLOR = (0xff, 0xff, 0xff)

PEARL_INNER_LAYER_COLORS = [
    (0x40, 0xff, 0xff),
    (0x40, 0xdd, 0xdd),
    (0x40, 0xbb, 0xbb),
    (0x40, 0x99, 0x99),
]

PEARL_OUTER_LAYER_COLORS = [
    (0xff, 0xff, 0x20),
    (0xdd, 0xdd, 0x20),
    (0xbb, 0xbb, 0x20),
    (0x99, 0x99, 0x20),
]

def _planner_is_big_cave(planner: Planner):
  return (
      (isinstance(planner, StemPlanner) and planner.kind == StemPlanner.CAVE)
      or isinstance(planner, BaseCavePlanner))

def _planner_border_color(planner: Planner) -> Color:
  if isinstance(planner, StemPlanner):
    if planner.fluid_type:
      return planner.fluid_type.inspect_color
    if planner.kind == StemPlanner.CAVE:
      return (0x77, 0x00, 0x10)
    return (0x44, 0x00, 0x08)
  assert isinstance(planner, SomaticPlanner)
  return planner.inspect_color

def _planner_bg_color(planner: Planner) -> Color:
  if isinstance(planner, StemPlanner):
    if planner.kind == StemPlanner.CAVE:
      return (0x77, 0x00, 0x10)
    return (0x44, 0x00, 0x08)
  assert isinstance(planner, SomaticPlanner)
  if planner.fluid_type:
    return planner.fluid_type.inspect_color
  return Tile.FLOOR.inspect_color

def _planner_fg_color(planner: Planner) -> Color:
  if isinstance(planner, StemPlanner) or planner.fluid_type:
    return (0xff, 0xff, 0xff)
  assert isinstance(planner, SomaticPlanner)
  return planner.inspect_color

def _planner_label_radius(planner: Planner, border_thickness):
  if _planner_is_big_cave(planner):
    return planner.pearl_radius - border_thickness
  return v.s(1)

def _planner_line_radius(planner: Planner, border_thickness):
  if _planner_is_big_cave(planner):
    return v.s(min(bp.pearl_radius for bp in planner.baseplates))
  if isinstance(planner, StemPlanner):
    if planner.kind == StemPlanner.CAVE:
      return v.s(1)
    return 0
  return v.s(0.5)

def _origin(planner):
  if _planner_is_big_cave(planner):
    return max(planner.baseplates, key=lambda bp: bp.pearl_radius).center
  return planner.center

def _draw_planner(canvas, planner):
  z_border, z_bg, z_fg = 0, 1, 2
  origin = _origin(planner)

  border_color = _planner_border_color(planner)
  bg_color = _planner_bg_color(planner)
  fg_color = _planner_fg_color(planner)

  border_thickness = v.a(2)
  label_radius = _planner_label_radius(planner, border_thickness)
  line_radius = _planner_line_radius(planner, border_thickness)

  # Center circle with label
  canvas.push(Circle(
      color=border_color,
      origin=origin,
      radius=label_radius + border_thickness), z_border)
  canvas.push(Circle(
      color=bg_color,
      origin=origin,
      radius=label_radius), z_bg)
  canvas.push(Label(
      font=FONT_TINY,
      text=f'{planner.id:d}',
      color=_planner_fg_color(planner),
      origin=origin,
      gravity=Gravity.CENTER), z_fg)

  # Border lines
  for a, b in itertools.pairwise(planner.baseplates):
    canvas.push(Line(
        color=border_color,
        start=a.center,
        end=b.center,
        thickness=(line_radius + border_thickness) * 2), z_border)
    if line_radius:
      canvas.push(Line(
          color=bg_color,
          start=a.center,
          end=b.center,
          thickness=line_radius * 2), z_bg)
  
  # Additional circles to connect lines together in a less jarring fashion
  if len(planner.baseplates) > 1:
    for bp in planner.baseplates:
      canvas.push(Circle(
          color=border_color,
          origin=bp.center,
          radius = line_radius + border_thickness), z_border)
      if line_radius:
        canvas.push(Circle(
            color=bg_color,
            origin=bp.center,
            radius=line_radius), z_bg)

def push_planners(canvas: Canvas, planners):
  st_pc = Canvas()
  so_pc = Canvas()
  for planner in planners:
    if isinstance(planner, StemPlanner):
      _draw_planner(st_pc, planner)
    else:
      assert isinstance(planner, SomaticPlanner)
      if not planner.pearl:
        _draw_planner(so_pc, planner)
  canvas.push(st_pc.freeze(), Z_PLANNERS)
  canvas.push(so_pc.freeze(), Z_PLANNERS)