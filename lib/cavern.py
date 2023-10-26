from collections.abc import Callable
from typing import Any, Dict, Iterable, List, Optional, Tuple, Set

import collections
import itertools
import math
import random
import time
import typing

from lib.outlines import Path, Space, Bubble, Baseplate
from lib.planners import Conquest, Planner, SomaticPlanner, StemPlanner
from lib.plastic import Diorama, serialize, Tile
from lib.utils.delaunay import slorp

class Cavern(object):
  def __init__(self, context):
    # Context object, which contains value tweaks and RNG
    self.context = context

    # Actual content data, which steps will fill in
    self.bubbles:    List[Bubble] = []
    self.baseplates: List[Baseplate] = []
    self.paths:      List[Path] = []
    self.conquest:   Optional[Conquest] = None
    self._diorama = Diorama(context)

  @property
  def spaces(self) -> List[Space]:
    return self.baseplates or self.bubbles

  @property
  def planners(self) -> Iterable[Planner]:
    return self.conquest.planners if self.conquest else tuple()

  @property
  def diorama(self) -> Diorama:
    return self._diorama

  def generate(self, logger):
    """Generates the cavern."""
    stages: Tuple[Tuple[str, Callable[[], None]]] = (
      # I. Outlines
      # Roughly based on this algorithm:
      # https://www.gamedeveloper.com/programming/procedural-dungeon-generation-algorithm

      # Generate "bubbles", which are rectangles of arbitrary sizes, and
      # place them roughly in a random pile in the center of the map.
      ('bubble',       self._bubble),
      # Perform a basic physics simulation to push overlapping bubbles apart
      # until those bubbles no longer overlap.
      ('separate',     self._separate),
      # Replace the bubbles with "baseplates", rounding all edges to the
      # nearest tile. These will become the foundation caves are built on.
      ('rasterize',    self._rasterize),
      # Choose the largest lots to become "special".
      ('discriminate', self._discriminate),
      # Create a triangular mesh between the centers of all special lots.
      # These will be treated as the non-overlapping edges of a graph,
      # with nodes at each special lot.
      ('triangulate',  self._triangulate),
      # Compute the minimum spanning tree of the graph generated above.
      # This ensures the graph is fully connected, so the cavern will
      # actually be playable.
      ('span',         self._span),
      # Add a few edges back in to make the cave more interesting.
      # Discard the remaining edges.
      ('weave',        self._weave),
      # Edges connect two special lots with a straight line. To make this more
      # interesting, add back any lots the edge intersects, forming a
      # zigzagging path between the two. Discard any remaining baseplates that
      # aren't part of a path.
      ('bore',         self._bore),

      # II. Planners

      # Assign the paths and special lots to "planners", which will decide
      # what to put in the lots they are given.
      ('negotiate',    self._negotiate),
      # Pick some planners and hint they should primarily contain water or
      # lava. Perform a depth-first search so the result will have more rivers \
      # than single lakes.
      ('flood',        self._flood),
      # The planners we have so far are basically stem cells.
      # Do a breadth-first search starting from the spawn and choose more
      # concretely what type of planner each cave and hall will be.
      ('conquest',     self._conquest),
      # Place tiles in the rough shape of each planner's layout.
      # Because planners overlap, some overwriting is expected.
      ('rough',        self._rough),
      # Do a second pass with planners placing everything else they want to
      # have in the level.
      ('fine',         self._fine),
      # Compute the final bounds of the level.
      ('fence',        self._fence),
    )

    for stage, fn in stages:
      self.context.stage = stage
      r = fn()
      if r:
        # THIS LINE IS IMPORTANT!
        # Need to iterate through r even if there is no logger
        for item in r:
          if logger:
            logger.log(self, stage, item)
      else:
        logger.log(self, stage, None)
    self.context.stage = 'done'
    logger.log(self, 'done', None)

  def is_done(self) -> bool:
    return self.context.stage == 'done'

  def _bubble(self):
    """Randomly place randomly sized rectangular bubbles near the center."""
    self.bubbles = [
      Bubble.from_rng(i, self.context)
      for i in range(self.context.bubble_count)]

  def _separate(self):
    """Push bubbles apart until they don't overlap."""
    counter = itertools.count()
    while Bubble.nudge_overlapping(self.bubbles):
      if next(counter) > 1000:
        raise 'probably not going to halt'
      yield
  
  def _rasterize(self):
    """Round bubbles to the nearest grid coordinate to make baseplates."""
    self.baseplates = [Baseplate(bubble, self.context) for bubble in self.bubbles]
 
  def _discriminate(self):
    """Choose the largest lots to become special."""
    special_count = round(len(self.baseplates) * self.context.special_lot_ratio)
    for baseplate in sorted(
        self.baseplates,
        key=Baseplate.area,
        reverse=True)[:special_count]:
      baseplate.kind = Baseplate.SPECIAL

  def _triangulate(self):
    """Generate halls between the special lots."""
    c = itertools.count()
    self.paths = [
      Path(next(c), self.context, (b1, b2))
      for (b1, b2) in slorp(
          tuple(s for s in self.baseplates if s.kind == Baseplate.SPECIAL))]
  
  def _span(self):
    """Find the minimum spanning tree between baseplates."""
    Path.minimum_spanning_tree(self.paths)

  def _weave(self):
    """Randomly choose some non-spanning graph edges to keep."""
    for path in self.paths:
      if path.kind == Path.AMBIGUOUS:
        path.weave()

  def _bore(self):
    Path.bore(self.paths, self.baseplates)

  def _negotiate(self):
    """Give lots to planners"""
    self.conquest = Conquest(
        self.context,
        StemPlanner.from_outlines(self.context, self.paths, self.baseplates))

  def _flood(self):
    self.conquest.flood()
  
  def _conquest(self):
    yield from self.conquest.conquest()

  def _rough(self):
    for planner in self.conquest.somatic_planners:
      planner.rough(self.diorama.tiles)
      yield

  def _fine(self):
    for planner in self.conquest.somatic_planners:
      planner.fine(self.diorama)

  def _fence(self):
    left   = min(x for x, _ in self.diorama.tiles) - 1
    top    = min(y for _, y in self.diorama.tiles) - 1
    width  = max(x for x, _ in self.diorama.tiles) + 2 - left
    height = max(y for _, y in self.diorama.tiles) + 2 - top
    # Manic Miners 1.0 can't handle non-square caverns,
    # so make this a square.
    if height > width:
      left -= (height - width) // 2
      width = height
    elif width > height:
      top -= (width - height) // 2
      height = width
    self.diorama.bounds = (left, top, width, height)

  def serialize(self):
    return self.diorama.serialize()