from collections.abc import Callable
from typing import Any, Dict, Iterable, List, Optional, Tuple, Set

import collections
import itertools
import math
import random
import time
import typing

from lib.base import NotHaltingError
from lib.lore import Lore
from lib.outlines import Path, Space, Bubble, Baseplate
from lib.planners import Conquest, Planner, SomaticPlanner, StemPlanner
from lib.plastic import Diorama, Objective, ResourceObjective, serialize, Tile
from lib.utils.cleanup import patch
from lib.utils.delaunay import slorp

class Cavern(object):
  def __init__(self, context):
    # Context object, which contains value tweaks and RNG
    self.context = context

    # Actual content data, which steps will fill in
    self.bubbles:     List[Bubble] = []
    self.baseplates:  List[Baseplate] = []
    self.paths:       List[Path] = []
    self.conquest:    Optional[Conquest] = None
    self._diorama:    Diorama = Diorama(context)
    self._serialized: Optional[str] = None

  @property
  def spaces(self) -> List[Space]:
    return self.baseplates or self.bubbles

  @property
  def planners(self) -> Iterable[Planner]:
    return self.conquest.planners if self.conquest else tuple()

  @property
  def diorama(self) -> Diorama:
    return self._diorama

  @property
  def serialized(self) -> Optional[str]:
    return self._serialized

  def generate(self):
    """Generates the cavern."""
    stages: Tuple[Tuple[str, Callable[[], None]]] = (
      # I. Outlines
      # Determine the approximate size and location of the caves in this
      # cavern, as well as the set of paths that will connect them.
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
      # Edges connect two special lots with a straight line. To make this more
      # interesting, add back any lots the edge intersects, forming a
      # zigzagging path between the two.
      ('bore',         self._bore),
      # Add a few edges back in to make the cave more interesting.
      # Discard the remaining edges.
      ('weave',        self._weave),
      # Discard any remaining baseplates that aren't part of a path.
      ('cull',         self._cull),

      # II. Planners
      # Using the outline as a guide, decide what to do with, then build each
      # individual cave and hall.

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
      # Reinforce any wall that would immediately collapse.
      ('patch',        self._patch),
      # Do a second pass with planners placing everything else they want to
      # have in the level.
      ('fine',         self._fine),

      # III. Polish
      # Look at the entire level to make sure it all fits together, then do
      # some final steps to put everything in the right place.

      # Figure out which tiles are discovered at the beginning of the level.
      ('discover',     self._discover),
      # Determine the objectives for the level.
      ('adjure',       self._adjure),
      # Write the objectives
      ('enscribe',     self._enscribe),
      # Add scripting logic
      ('script',       self._script),
      # Compute the final bounds of the level.
      ('fence',        self._fence),
      # Serialize the output
      ('serialize',    self._serialize),
    )
    try:
      self.context.logger.log_stage(
          'init', 0, len(stages), None)
      for i, (stage, fn) in enumerate(stages):
        r = fn()
        if r:
          # THIS LINE IS IMPORTANT!
          # Need to iterate through r even if there is no logger
          for details in r:
            self.context.logger.log_stage(
                stage, i, len(stages), details)
        else:
          self.context.logger.log_stage(
              stage, i, len(stages), None)
      self.context.logger.log_stage(
          'done', len(stages), len(stages), None)
    except Exception as e:
      self.context.logger.log_exception(e)
      raise

  def is_done(self) -> bool:
    return self._serialized is not None

  def _bubble(self):
    """Randomly place randomly sized rectangular bubbles near the center."""
    self.bubbles = [
      Bubble.from_rng(i, self.context)
      for i in range(self.context.bubble_count)]

  def _separate(self):
    """Push bubbles apart until they don't overlap."""
    for i in range(300):
      moving = Bubble.nudge_overlapping(self.bubbles)
      yield
      if not moving:
        break
    else:
      raise NotHaltingError(f'Separation failed to halt after 300 iterations')
  
  def _rasterize(self):
    """Round bubbles to the nearest grid coordinate to make baseplates."""
    self.baseplates = [Baseplate(bubble, self.context) for bubble in self.bubbles]
 
  def _discriminate(self):
    """Choose the largest lots to become special."""
    for baseplate in sorted(
        self.baseplates,
        key=Baseplate.area,
        reverse=True)[:self.context.special_baseplate_count]:
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

  def _bore(self):
    """Add unused baseplates to paths they intersect."""
    Path.bore(self.paths, self.baseplates)

  def _weave(self):
    """Randomly choose some non-spanning graph edges to keep."""
    Path.weave(self.context, self.paths)

  def _cull(self):
    for bp in self.baseplates:
      if bp.kind == Baseplate.AMBIGUOUS:
        bp.kind = Baseplate.EXCLUDED

  def _negotiate(self):
    """Give baseplates to planners."""
    self.conquest = Conquest(
        self.context,
        StemPlanner.from_outlines(self.context, self.paths, self.baseplates))

  def _flood(self):
    """Put water and lava in some planners."""
    self.conquest.flood()
  
  def _conquest(self):
    """Move outward from spawn and decide how to specialize planners."""
    yield from self.conquest.conquest()

  def _rough(self):
    """Do a rough draft of tile placement that may be overwritten."""
    for planner in self.conquest.somatic_planners:
      planner.rough(self.diorama.tiles)
      yield planner

  def _patch(self):
    """Fix walls that would immediately collapse on load."""
    patch(self.diorama.tiles)

  def _fine(self):
    """Put anything else in the level the planners want to have."""
    for planner in self.conquest.somatic_planners:
      planner.fine(self.diorama)

  def _discover(self):
    """Make discovered caverns visible at start."""
    self.diorama.discover()

  def _adjure(self):
    """Figure out objectives for the level."""
    def gen():
      for planner in self.conquest.somatic_planners:
        yield from planner.objectives
    objs = list(Objective.uniq(gen()))
    # If none of the caverns have objectives, generate one to collect a
    # reasonable number of crystals.
    crystals = math.floor(
        self.diorama.total_crystals * self.context.crystal_goal_ratio)
    crystals -= (crystals % 5)
    if (not objs
        or (len(objs) == 1
            and isinstance(objs[0], ResourceObjective)
            and not objs[0].ore
            and not objs[0].studs
            and objs[0].crystals < crystals)):
      objs = [ResourceObjective(crystals=crystals)]
    self.diorama.objectives.extend(objs)

  def _enscribe(self):
    """Generate copy for briefings, etc..."""
    lore = Lore(self)
    self.diorama.briefing = lore.briefing()
    self.diorama.briefing_success = lore.success()
    self.diorama.briefing_failure = lore.failure()
    self.diorama.level_name = lore.level_name()

  def _script(self):
    """Write scripts."""
    for planner in self.conquest.somatic_planners:
      planner.script(self.diorama)

  def _fence(self):
    """Compute the final bounds of the level."""
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

  def _serialize(self):
    """Dump everything to a string."""
    self._serialized = self.diorama.serialize()