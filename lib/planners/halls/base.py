import itertools

from lib.planners.base import SomaticPlanner
from lib.plastic import Tile

class BaseHallPlanner(SomaticPlanner):

  def walk(self):
    return self.walk_pearl(self.walk_stream(), 3)

  def rough(self, tiles):
    for (x, y), layer in self.walk():
      tiles[x, y] = (Tile.POWER_PATH, Tile.FLOOR, Tile.LOOSE_ROCK)[layer]

  def fine(self, diorama):
    pass