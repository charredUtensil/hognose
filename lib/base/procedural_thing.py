from .context import Context
from .thing_random import ThingRandom

class ProceduralThing(object):

  def __init__(self, id: int, context: Context):
    self._id = id
    self._context = context

  @property
  def id(self) -> int:
    return self._id

  @property
  def context(self) -> Context:
    return self._context

  @property
  def rng(self) -> ThingRandom:
    return self._context.rng(self._id)