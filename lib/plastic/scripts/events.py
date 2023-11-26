from typing import Literal, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from ..creatures import Creature

class Event(object):
  pass

class Call(Event):
  def __init__(self):
    pass

class Emerge(Event):
  """Causes a monster to emerge."""

  def __init__(
      self,
      pos: Tuple[int, int],
      creature_type: Literal[
        'Creature.Type.ROCK_MONSTER',
        'Creature.Type.ICE_MONSTER',
        'Creature.Type.LAVA_MONSTER'],
      distance: int,
      direction: Literal['A', 'N', 'E', 'S', 'W'] = 'A'):
    self.pos = pos
    self.distance = distance
    self.creature_type = creature_type
    self.direction = direction

  def serialize(self, offset: Tuple[int, int]):
    ox, oy = offset
    x, y = self.pos

    return (
      f'emerge:{x + ox:d},{y + oy:d},'
      f'{self.direction},{self.creature_type},{self.distance:d}')