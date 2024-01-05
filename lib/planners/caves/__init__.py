from . import empty, flooded, lost_miners, simple_spawn, treasure
from .empty import EmptyCavePlanner
from .flooded import FloodedCavePlanner
from .lost_miners import LostMinersCavePlanner
from .simple_spawn import SimpleSpawnCavePlanner
from .treasure import HoardCavePlanner, NougatCavePlanner, TreasureCavePlanner

CAVE_BIDDERS = (
    empty.bids,
    flooded.bids,
    lost_miners.bids,
    treasure.bids,
)

SPAWN_BIDDERS = (
    simple_spawn.bids,
)