from typing import Tuple

import math
import enum

from lib.plastic.entities import Entity
from lib.plastic.position import Position
from lib.base import Biome


class Creature(Entity):

  class Type(enum.Enum):
    ROCK_MONSTER = 'CreatureRockMonster_C'
    ICE_MONSTER = 'CreatureIceMonster_C'
    LAVA_MONSTER = 'CreatureLavaMonster_C'
    SLIMY_SLUG = 'CreatureSlimySlug_C'
    SMALL_SPIDER = 'CreatureSmallSpider_C'
    BAT = 'CreatureBat_C'

  @staticmethod
  def monster_type_for_biome(biome: Biome) -> 'Creature.Type':
    return MONSTER_FOR_BIOME[biome]

  def __init__(
      self,
      id: int,
      type: 'Creature.Type',
      position: Position,
      sleep: bool = False):
    super().__init__(position)
    self.id = id
    self.type = type
    self.sleep = sleep

  def serialize(self, offset: Tuple[int, int]):
    return (
        f'{self.type.value}\n'
        f'{self.position.serialize(offset, math.pi / 2)}\n'
        f'ID={self.id}{",Sleep=true" if self.sleep else ""}')


MONSTER_FOR_BIOME = {
    Biome.ROCK: Creature.Type.ROCK_MONSTER,
    Biome.ICE: Creature.Type.ICE_MONSTER,
    Biome.LAVA: Creature.Type.LAVA_MONSTER,
}
