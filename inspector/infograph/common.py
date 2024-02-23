import itertools

from inspector.canvas import Font, v

FONT_TINY = Font('monospace', 10, bold=True)
FONT_MED  = Font('trebuchetms', 16, bold=True)
FONT_BIG  = Font('trebuchetms', 24, bold=True)

OVERLAY_COLOR = (0x44, 0xff, 0x88)
OVERLAY_SHADOW_COLOR = (0x00, 0x00, 0x00)
WARNING_COLOR = (0xff, 0xff, 0x00)

OVERLAY_PADDING = v.a(10)
OVERLAY_SHADOW_OFFSET = v.a(2)

_z = itertools.count()
Z_BACKGROUND = next(_z)
Z_BOUNDS = next(_z)
Z_SPACES = next(_z)
Z_PATHS = next(_z)
Z_PLANNERS = next(_z)
Z_TILES = next(_z)
Z_ORE = next(_z)
Z_HAZARDS = next(_z)
Z_CRYSTALS = next(_z)
Z_ENTITIES = next(_z)
Z_PEARL = next(_z)
Z_SCRIPT = next(_z)
Z_OVERLAY = next(_z)