from typing import Iterable, List, Set, Tuple

import re

MACRO_RE = re.compile(r'(?P<name>[x|y])@(?P<value>-?\d+)')

class Script():

  def __init__(self):
    self._fragments: List['ScriptFragment'] = []
    self.flags: Set[str] = set()

  def __len__(self):
    return sum(len(sf) for sf in self._fragments)

  def __str__(self):
    return '\n'.join(str(sf) for sf in self._fragments)

  def add(self, fragment: 'ScriptFragment'):
    self._fragments.append(fragment)

  def serialize(self, offset: Tuple[int, int]):
    raw = '\n'.join(str(sf) for sf in self._fragments)
    ox, oy = offset
    def fx(v: str):
      return ox + int(v)
    def fy(v: str):
      return oy + int(v)
    macros = {'x': fx, 'y': fy}
    def macro(m):
      return str(macros[m.group('name')](m.group('value')))
    return MACRO_RE.sub(macro, raw)

  @staticmethod
  def escape_string(s: str) -> str:
    return s.replace('"', '\\"').replace('\n', '\\n')

class ScriptFragment():

  def __init__(self, lines: Iterable[str]):
    self._lines = tuple(lines)

  def __str__(self):
    return '\n'.join(self._lines)

  def __len__(self):
    return len(self._lines)

  def __add__(self, other):
    if not other:
      return self
    if isinstance(other, ScriptFragment):
      return ScriptFragment(self._lines + other._lines)
    return NotImplemented

  def __radd__(self, other):
    return self.__add__(other)