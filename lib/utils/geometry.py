from typing import Iterable, Tuple

import math

def adjacent(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
  xa, ya = a
  xb, yb = b
  return (
    (xa == xb and ya in range(yb - 1, yb + 2)) or
    (ya == yb and xa in range(xb - 1, xb + 2)))

def plot_line(a, b) -> Iterable[Tuple[int, int]]:
  x0, y0 = math.floor(a[0]), math.floor(a[1])
  x1, y1 = math.floor(b[0]), math.floor(b[1])
  dx = abs(x1 - x0)
  sx = 1 if x0 < x1 else -1
  dy = -abs(y1 - y0)
  sy = 1 if y0 < y1 else -1
  error = dx + dy
  
  while True:
    yield (x0, y0)
    if x0 == x1 and y0 == y1:
      break
    e2 = 2 * error
    if e2 >= dy:
        if x0 == x1:
          break
        error = error + dy
        x0 = x0 + sx
    if e2 <= dx:
        if y0 == y1:
          break
        error = error + dx
        y0 = y0 + sy
  yield (x1, y1)