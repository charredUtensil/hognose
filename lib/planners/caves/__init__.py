from . import empty, lost_miners, simple_spawn, treasure
from .empty import EmptyCavePlanner
from .lost_miners import LostMinersCavePlanner
from .simple_spawn import SimpleSpawnCavePlanner
from .treasure import HoardCavePlanner, NougatCavePlanner, TreasureCavePlanner

CAVE_BIDDERS = (
    empty.bids,
    lost_miners.bids,
    treasure.bids,
)

SPAWN_BIDDERS = (
    simple_spawn.bids,
)