from typing import Literal

from .context import Context
from .pseudorandom import KINDS, Rng

class ProceduralThing(object):

  def __init__(self, id: int, context: Context):
    self._id = id
    self._context = context
    self.rng = BoundDiceBox(self)

  @property
  def id(self) -> int:
    return self._id

  @property
  def context(self) -> Context:
    return self._context

class BoundDiceBox(object):
  def __init__(self, thing: ProceduralThing):
    self._thing = thing

  def __getitem__(self, kind: Literal[KINDS]):
    return self._thing._context.rng[kind, self._thing._id]
