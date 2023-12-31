from typing import Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from lib import Cavern

import abc
import sys
import traceback

class Logger(abc.ABC):

  def __init__(self):
    self._walks = []

  def log_stage(self, stage: str, index: int, total_stages: int, details: Any):
    pass

  def log_warning(self, message: str):
    print(f'warning: {message}', file=sys.stderr)

  def log_exception(self, e: Exception):
    print(
        ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
        file=sys.stderr)