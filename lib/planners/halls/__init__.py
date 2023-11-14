from . import empty, thin
from .empty import EmptyHallPlanner
from .thin import ThinHallPlanner

HALL_BIDDERS = (
    empty.bids,
    thin.bids,
)