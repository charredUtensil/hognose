
class NotHaltingError(Exception):
  """Raised when a step with an indeterminate number of steps fails to halt."""
  pass

class SoftLockedError(Exception):
  """Raised when the cave is unwinnable and can't be made winnable."""
  pass