class Position(object):
  ENTITY_SCALE = 300

  def __init__(self, translation, rotation, scale=(1, 1, 1)):
    self.tx, self.ty, self.tz = translation
    self.rp, self.ry, self.rr = rotation
    self.sx, self.sy, self.sz = scale

  def serialize(self, offset):
    tx = (self.tx + offset[0]) * Position.ENTITY_SCALE
    ty = (self.ty + offset[0]) * Position.ENTITY_SCALE
    tz = self.tz
    return (
      f'Translation: X={tx:.3f} Y={ty:.3f} Z={tz:.3f} '
      f'Rotation: P={self.rp:.6f} Y={self.ry:.6f} R={self.rr:.6f} '
      f'Scale X={self.sx:.3f} Y={self.sy:.3f} Z={self.sz:.3f}'
    )