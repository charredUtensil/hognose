from collections.abc import Callable
from typing import Iterable, List, Optional, Tuple

import itertools

from lib.base import GenerationError
from lib.holistics import Adjurator, patch
from lib.lore import Lore
from lib.outlines import Path, Bubble, Baseplate, Partition
from lib.planners import Conquest, Planner, StemPlanner
from lib.plastic import Diorama, ScriptFragment
from lib.utils.delaunay import slorp

V_DONE = 1
V_MAJOR = 2
V_MINOR = 3
V_VERBOSE = 4


class Cavern(): # pylint: disable=too-many-instance-attributes
  def __init__(self, context):
    # Context object, which contains value tweaks and RNG
    self.context = context

    # Actual content data, which steps will fill in
    self.stage: str = 'init'
    self.bubbles: List[Bubble] = []
    self.baseplates: List[Baseplate] = []
    self.paths: List[Path] = []
    self.conquest: Optional[Conquest] = None
    self._diorama: Diorama = Diorama(context)
    self._serialized: Optional[str] = None
    self.adjurator: Optional[Adjurator] = None
    self._lore: Optional[Lore] = None

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
      ('partition', self._partition),
      # Choose the largest lots to become "special".
      ('discriminate', self._discriminate),
      # Create a triangular mesh between the centers of all special lots.
      # These will be treated as the non-overlapping edges of a graph,
      # with nodes at each special lot.
      ('triangulate', self._triangulate),
      # Compute the minimum spanning tree of the graph generated above.
      # This ensures the graph is fully connected, so the cavern will
      # actually be playable.
      ('span', self._span),
      # Edges connect two special lots with a straight line. To make this more
      # interesting, add back any lots the edge intersects, forming a
      # zigzagging path between the two.
      ('bore', self._bore),
      # Add a few edges back in to make the cave more interesting.
      # Discard the remaining edges.
      ('weave', self._weave),
      # Discard any remaining baseplates that aren't part of a path.
      ('cull', self._cull),

      # II. Planners
      # Using the outline as a guide, decide what to do with, then build each
      # individual cave and hall.

      # Assign the paths and special lots to "planners", which will decide
      # what to put in the lots they are given.
      ('negotiate', self._negotiate),
      # Pick some planners and hint they should primarily contain water or
      # lava. Perform a depth-first search so the result will have more rivers \
      # than single lakes.
      ('flood', self._flood),
      # The planners we have so far are basically stem cells.
      # Do a breadth-first search starting from the spawn and choose more
      # concretely what type of planner each cave and hall will be.
      ('conquest', self._conquest),
      # Place tiles in the rough shape of each planner's layout.
      # Because planners overlap, some overwriting is expected.
      ('rough', self._rough),
      # Reinforce any wall that would immediately collapse.
      ('patch', self._patch),
      # Do a second pass with planners placing everything else they want to
      # have in the level.
      ('fine', self._fine),

      # III. Polish
      # Look at the entire level to make sure it all fits together, then do
      # some final steps to put everything in the right place.

      # Figure out which tiles are discovered at the beginning of the level.
      ('discover', self._discover),
      # Determine the objectives for the level.
      ('adjure', self._adjure),
      # Write the objectives.
      ('enscribe', self._enscribe),
      # Add scripting logic.
      ('script', self._script),
      # Compute the final bounds of the level.
      ('fence', self._fence),
      # Serialize the output.
      ('serialize', self._serialize),
    )
    try:
      self._log_state(V_MINOR)
      for i, (stage, fn) in enumerate(stages):
        self.stage = stage
        fn()
        self.context.logger.log_progress(i / (len(stages) - 1))
      self.stage = 'done'
      self._log_state(V_DONE)
    except Exception as e:
      self.context.logger.log_progress(1)
      self.context.logger.log_exception(self, e)
      raise GenerationError() from e

  def is_done(self) -> bool:
    return self._serialized is not None

  def _log_state(self, verbosity, details=None):
    self.context.logger.log_state(self, verbosity, details)

  def _partition(self):
    """Randomly place randomly sized rectangular bubbles near the center."""
    partition = Partition(self.context)
    self.bubbles = partition.bubbles
    self.baseplates = partition.baseplates
    self._log_state(V_MINOR)
    while partition.bubbles:
      partition.step()
      self._log_state(V_MINOR)

  def _discriminate(self):
    """Choose the largest lots to become special."""
    for baseplate in sorted(
        self.baseplates,
        key=lambda bp: bp.area,
        reverse=True)[:self.context.special_baseplate_count]:
      baseplate.kind = Baseplate.SPECIAL
    self._log_state(V_MINOR)

  def _triangulate(self):
    """Generate halls between the special lots."""
    c = itertools.count()
    self.paths = [
      Path(next(c), self.context, (b1, b2))
      for (b1, b2) in slorp(
          tuple(s for s in self.baseplates if s.kind == Baseplate.SPECIAL))]
    self._log_state(V_MINOR)

  def _span(self):
    """Find the minimum spanning tree between baseplates."""
    Path.minimum_spanning_tree(self.paths)
    self._log_state(V_MAJOR)

  def _bore(self):
    """Add unused baseplates to paths they intersect."""
    Path.bore(self.paths, self.baseplates)
    self._log_state(V_MINOR)

  def _weave(self):
    """Randomly choose some non-spanning graph edges to keep."""
    for _ in Path.weave(self.context, self.paths):
      self._log_state(V_MINOR)

  def _cull(self):
    for bp in self.baseplates:
      if bp.kind == Baseplate.AMBIGUOUS:
        bp.kind = Baseplate.EXCLUDED
    self._log_state(V_MAJOR)

  def _negotiate(self):
    """Give baseplates to planners."""
    self.conquest = Conquest(
        self.context,
        StemPlanner.from_outlines(self.context, self.paths, self.baseplates))
    self._log_state(V_MINOR)

  def _flood(self):
    """Put water and lava in some planners."""
    self.conquest.flood()
    self._log_state(V_MAJOR)

  def _conquest(self):
    """Move outward from spawn and decide how to specialize planners."""
    last = None
    for planner in self.conquest.conquest():
      self._log_state(V_MINOR, last)
      last = planner
    self._log_state(V_MAJOR, last)

  def _rough(self):
    """Do a rough draft of tile placement that may be overwritten."""
    for planner in self.conquest.somatic_planners:
      planner.rough(self.diorama.tiles)
      self._log_state(V_MINOR, planner)
    self._log_state(V_MAJOR)

  def _patch(self):
    """Fix walls that would immediately collapse on load."""
    patch(self.diorama.tiles)
    self._log_state(V_MAJOR)

  def _fine(self):
    """Put anything else in the level the planners want to have."""
    for planner in self.conquest.somatic_planners:
      planner.fine(self.diorama)
      self._log_state(V_VERBOSE, planner)
    self._log_state(V_MAJOR)

  def _discover(self):
    """Make discovered caverns visible at start."""
    self.diorama.discover()
    self._log_state(V_MINOR)

  def _adjure(self):
    """Figure out objectives for the level."""
    self.adjurator = Adjurator(self.context)
    for planner in self.conquest.somatic_planners:
      planner.adjure(self.adjurator)
    self.adjurator.write(self.diorama)
    self._log_state(V_MINOR)

  def _enscribe(self):
    """Generate copy for briefings, etc..."""
    self._lore = Lore(self)
    self.diorama.briefing = self._lore.briefing
    self.diorama.briefing_success = self._lore.success
    self.diorama.briefing_failure = self._lore.failure
    self.diorama.level_name = self._lore.level_name
    self._log_state(V_MINOR)

  def _script(self):
    """Write scripts."""
    def h():
      yield self.adjurator.script(self.diorama, self._lore), self.adjurator
      for planner in self.conquest.somatic_planners:
        yield planner.script(self.diorama, self._lore), planner
    for sf, source in h():
      if sf:
        header = str(source)
        sf = ScriptFragment((
            f'# {"=" * len(header)}',
            f'# {header}',
            f'# {"=" * len(header)}')) + sf
        self._log_state(V_VERBOSE, sf)
        self.diorama.script.add(sf)
    self._log_state(V_MINOR)

  def _fence(self):
    """Compute the final bounds of the level."""
    left = min(x for x, _ in self.diorama.tiles) - 1
    top = min(y for _, y in self.diorama.tiles) - 1
    width = max(x for x, _ in self.diorama.tiles) + 2 - left
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
    self._log_state(V_MINOR)

  def _serialize(self):
    """Dump everything to a string."""
    self._serialized = self.diorama.serialize()
    self._log_state(V_MINOR)
