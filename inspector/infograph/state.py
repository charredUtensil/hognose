from inspector.canvas import Canvas, FrozenCanvas, DrawContext, Fill, Rect

from inspector.infograph.adjurator import push_adjurator
from inspector.infograph.common import Z_BACKGROUND
from inspector.infograph.map import push_map
from inspector.infograph.outlines import push_outlines
from inspector.infograph.overlays import OVERLAY_COLOR, push_overlays
from inspector.infograph.planners import push_planners
from inspector.infograph.scripts import push_script

def push_state(canvas, cavern, details, warnings):
  canvas.push(Fill(color=(0, 0, 0)), Z_BACKGROUND)
  if cavern.conquest:
    push_planners(canvas, cavern.conquest.planners, details)
  else:
    push_outlines(canvas, cavern.bubbles, cavern.baseplates, cavern.paths)
  push_map(canvas, cavern.diorama)
  if cavern.stage == 'adjure':
    push_adjurator(canvas, cavern.adjurator)
  push_script(canvas, details)
  push_overlays(canvas, cavern, details, warnings)