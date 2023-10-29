from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
  from lib import Cavern

import abc
import sys
import traceback

class Logger(abc.ABC):

  @abc.abstractmethod
  def log(self, cavern: 'Cavern', stage: str, item: Any):
    pass

  def log_warning(self, message: str):
    print(f'warning: {message}', file=sys.stderr)

  def log_exception(self, cavern: 'Cavern', e: Exception):
    print(f'error: Exception on seed {hex(cavern.context.seed)}', file=sys.stderr)
    print(
        ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
        file=sys.stderr)