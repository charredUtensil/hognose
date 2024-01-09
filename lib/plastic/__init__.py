"""Plastic (because LEGO) is anything that actually goes in the file."""

from .building import Building, BuildingDoesNotFitException
from .creatures import Creature
from .diorama import Diorama
from .hazards import Erosion, Landslide
from .miners import Miner
from .objectives import Objective, FindMinerObjective, ResourceObjective
from .position import Facing, Position
from .tile import BasicTile, Tile