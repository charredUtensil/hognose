from typing import Iterable, Tuple

import re

MACRO_RE = re.compile(r'(?P<name>[x|y])@(?P<value>-?\d+)')

class Script(object):

  def __init__(self):
    self._parts = []

  def append(self, part: str):
    self._parts.append(part)

  def extend(self, parts: Iterable[str]):
    self._parts.extend(parts)

  def serialize(self, offset: Tuple[int, int]):
    def lines():
      ox, oy = offset
      def macro(m):
        return str({'x': ox, 'y': oy}[m.group('name')] + int(m.group('value')))
      for p in self._parts:
        yield MACRO_RE.sub(macro, p)
    return '\n'.join(lines())