from typing import Any, TYPE_CHECKING

import abc
import sys
import traceback

if TYPE_CHECKING:
  from lib import Cavern

class Logger(abc.ABC):
  """A basic logger."""

  def __init__(self):
    self._walks = []

  def log_progress(self, progress: float):
    pass

  def log_state(self, cavern: 'Cavern', verbosity: int, details: Any):
    pass

  def log_warning(self, message: str):
    print(f'warning: {message}', file=sys.stderr)

  def log_exception(self, cavern: 'Cavern', e: Exception):
    print(
        ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
        file=sys.stderr)

class MultiCavernLogger(Logger):

  def __init__(self, proxied, index, count):
    self._proxied: Logger = proxied
    self._index: int = index
    self._count: int = count

  def log_progress(self, progress: float):
    self._proxied.log_progress((self._index + progress) / self._count)

  def log_state(self, *args, **kwargs):
    self._proxied.log_state(*args, **kwargs)

  def log_warning(self, *args, **kwargs):
    self._proxied.log_warning(*args, **kwargs)

  def log_exception(self, *args, **kwargs):
    self._proxied.log_exception(*args, **kwargs)