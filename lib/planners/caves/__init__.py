from . import empty, established_hq, flooded, lost_miners, simple_spawn, treasure
from .empty import EmptyCavePlanner
from .established_hq import EstablishedHQCavePlanner
from .flooded import FloodedCavePlanner
from .lost_miners import LostMinersCavePlanner
from .simple_spawn import SimpleSpawnCavePlanner
from .treasure import HoardCavePlanner, NougatCavePlanner, TreasureCavePlanner

CAVE_BIDDERS = (
    empty.bids,
    established_hq.bids,
    flooded.bids,
    lost_miners.bids,
    treasure.bids,
)

SPAWN_BIDDERS = (
    simple_spawn.bids,
    established_hq.spawn_bids,
)
