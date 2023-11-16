CreatureIceMonster_C
Translation: X=505.761 Y=1250.646 Z=137.150 Rotation: P=0.000000 Y=99.819389 R=0.000000 Scale X=1.000 Y=1.000 Z=1.000
ID=0
CreatureLavaMonster_C
Translation: X=845.957 Y=1269.523 Z=137.150 Rotation: P=0.000000 Y=-30.185892 R=0.000000 Scale X=1.000 Y=1.000 Z=1.000
ID=1
CreatureRockMonster_C
Translation: X=1476.177 Y=1316.475 Z=137.150 Rotation: P=0.000000 Y=-161.004059 R=0.000000 Scale X=1.000 Y=1.000 Z=1.000
ID=2
CreatureSlimySlug_C
Translation: X=1921.322 Y=1357.476 Z=62.150 Rotation: P=0.000000 Y=42.545879 R=0.000000 Scale X=1.000 Y=1.000 Z=1.000
ID=3
CreatureSmallSpider_C
Translation: X=501.000 Y=1860.707 Z=32.150 Rotation: P=0.000000 Y=-113.091141 R=0.000000 Scale X=1.000 Y=1.000 Z=1.000
ID=4
CreatureBat_C
Translation: X=1151.971 Y=1984.789 Z=27.150 Rotation: P=0.000000 Y=78.790764 R=0.000000 Scale X=1.000 Y=1.000 Z=1.000
ID=5

import enum

from .entities import Entity

class Creature(Entity):

  class Type(enum.Enum):
    ROCK_MONSTER = 'CreatureRockMonster_C'
    ICE_MONSTER = 'CreatureIceMonster_C'
    LAVA_MONSTER = 'CreatureLavaMonster_C'
    SLIMY_SLUG = 'CreatureSlimySlug_C'
    SMALL_SPIDER = 'CreatureSmallSpider_C'
    BAT = 'CreatureBat_C'

  def __init__(id: int, type: Creature.Type, position: Position):
    super().__init__(id, position)
    self.type = type

  def serialize(self, offset: Tuple[int, int]):
    return f'{self.type.value}\n{self.position.serialize(offset)}\nID={self.id}'