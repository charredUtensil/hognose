import abc

from lib.base.context import Context


class ProceduralThing(abc.ABC):
  """Base class for classes that use RNG."""

  def __init__(self, id, context):
    self._id: int = id
    self._context: Context = context
    self.rng = BoundDiceBox(self)

  @property
  def id(self) -> int:
    return self._id

  @property
  def context(self) -> Context:
    return self._context


class BoundDiceBox():
  """A binding of DiceBox that uses the ID from this ProceduralThing."""

  def __init__(self, thing: ProceduralThing):
    self._thing = thing

  def __getitem__(self, kind: str):
    return self._thing._context.rng[kind, self._thing._id]
