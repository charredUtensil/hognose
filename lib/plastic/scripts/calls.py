from .base import ScriptElement

class Call(ScriptElements):

  def __init__(self, occurrence: str, trigger, effect):
    self._occurrence = occurrence
    self._trigger = trigger
    self._effect = effect

  def serialize(self, offset):
    return f'{self._occurrence}({self._trigger}){self._effect}'