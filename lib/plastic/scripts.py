from typing import Iterable, List, Set, Tuple

import re

MACRO_RE = re.compile(r'(?P<name>[x|y])@(?P<value>-?\d+)')

class Script(object):

  def __init__(self):
    self._lines: List[str] = []
    self.flags: Set[str] = set()

  def append(self, line: str):
    self._lines.append(line)

  def extend(self, lines: Iterable[str]):
    self._lines.extend(lines)

  def __len__(self):
    return len(self._lines)

  def serialize(self, offset: Tuple[int, int]):
    def lines():
      ox, oy = offset
      def macro(m):
        return str({'x': ox, 'y': oy}[m.group('name')] + int(m.group('value')))
      for line in self._lines:
        yield MACRO_RE.sub(macro, line)
      yield ''
    return '\n'.join(lines())

  @staticmethod
  def escape_string(s: str) -> str:
    return s.replace('"', '\\"').replace('\n', '\\n')