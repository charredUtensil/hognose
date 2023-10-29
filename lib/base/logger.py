from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
  from .cavern import Cavern

import abc

class Logger(abc.ABC):

  @abc.abstractmethod
  def log(self, cavern: 'Cavern', stage: str, item: Any):
    pass

  @abc.abstractmethod
  def log_warning(self, message: str):
    pass

  @abc.abstractmethod
  def log_exception(self, cavern: 'Cavern', e: Exception):
    pass