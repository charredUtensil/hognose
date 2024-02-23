from inspector.canvas import Canvas, Circle
from lib.holistics import Adjurator

OBJECTIVE_COLOR = (0x00, 0xff, 0xff)


def push_adjurator(canvas: Canvas, adjurator: Adjurator):
  pc = Canvas()
  for x, y in adjurator.positions:
    pc.push(Circle(
        color=OBJECTIVE_COLOR,
        origin=(x + 0.5, y + 0.5),
        radius=5,
        thickness=2))
