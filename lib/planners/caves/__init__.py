from .empty import EmptyCavePlanner
from .spawn import SpawnCavePlanner
from .treasure import TreasureCavePlanner

CAVES = (EmptyCavePlanner, TreasureCavePlanner)
SPAWNS = (SpawnCavePlanner, )