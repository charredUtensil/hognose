from .base import ScriptElement

class Trigger(ScriptElement):
  pass

class Change(Trigger):

  def __init__(self, pos):
    self.pos = pos

  def serialize(self, offset):
    ox, oy = offset
    x, y = self.pos
    return f'change:{x + ox:d},{y + oy:d}'

class Enter(Trigger):

  def __init__(self, pos):
    self.pos = pos

  def serialize(self, offset):
    ox, oy = offset
    x, y = self.pos
    return f'enter:{x + ox:d},{y + oy:d}'