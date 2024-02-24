class GenerationError(Exception):
  """Raised when cavern.generate() fails."""

class NotHaltingError(Exception):
  """Raised when a step with an indeterminate number of steps fails to halt."""
