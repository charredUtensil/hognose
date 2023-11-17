from typing import Tuple

import enum

from .entities import Entity
from .position import Position

class Creature(Entity):

  class Type(enum.Enum):
    ROCK_MONSTER = 'CreatureRockMonster_C'
    ICE_MONSTER = 'CreatureIceMonster_C'
    LAVA_MONSTER = 'CreatureLavaMonster_C'
    SLIMY_SLUG = 'CreatureSlimySlug_C'
    SMALL_SPIDER = 'CreatureSmallSpider_C'
    BAT = 'CreatureBat_C'

  def __init__(self, id: int, type: 'Creature.Type', position: Position):
    super().__init__(position)
    self.id = id
    self.type = type

  def serialize(self, offset: Tuple[int, int]):
    return f'{self.type.value}\n{self.position.serialize(offset)}\nID={self.id}'