from .position import Position


class Entity():
  def __init__(self, position: Position):
    self.position = position

  @property
  def x(self):
    return self.position.tx

  @property
  def y(self):
    return self.position.ty

  @property
  def theta(self):
    return self.position.ry
