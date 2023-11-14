from . import empty, lost_miners, spawn, treasure
from .empty import EmptyCavePlanner
from .lost_miners import LostMinersCavePlanner
from .spawn import SpawnCavePlanner
from .treasure import HoardCavePlanner, NougatCavePlanner, TreasureCavePlanner

CAVE_BIDDERS = (
    empty.bids,
    lost_miners.bids,
    treasure.bids,
)

SPAWN_BIDDERS = (
    spawn.bids,
)