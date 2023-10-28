from typing import Iterable, Tuple

def plot_line(a, b) -> Iterable[Tuple[int, int]]:
  x0, y0 = round(a[0]), round(a[1])
  x1, y1 = round(b[0]), round(b[1])
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