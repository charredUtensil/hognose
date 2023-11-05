from .empty import EmptyCavePlanner
from .lost_miners import LostMinersCavePlanner
from .spawn import SpawnCavePlanner
from .treasure import TreasureCavePlanner

CAVES = (EmptyCavePlanner, LostMinersCavePlanner, TreasureCavePlanner)
SPAWNS = (SpawnCavePlanner, )