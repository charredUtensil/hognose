from typing import Iterable, Tuple

import math

def adjacent(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
  xa, ya = a
  xb, yb = b
  return (
    (xa == xb and ya in range(yb - 1, yb + 2)) or
    (ya == yb and xa in range(xb - 1, xb + 2)))

def plot_line(a, b, contiguous = False) -> Iterable[Tuple[int, int]]:
  x, y = math.floor(a[0]), math.floor(a[1])
  dest_x, dest_y = math.floor(b[0]), math.floor(b[1])
  dx = abs(dest_x - x)
  sx = 1 if x < dest_x else -1
  dy = -abs(dest_y - y)
  sy = 1 if y < dest_y else -1
  error = dx + dy
  
  while True:
    yield (x, y)
    if x == dest_x and y == dest_y:
      break
    e2 = 2 * error
    move_x = e2 >= dy
    move_y = e2 <= dx
    if move_x:
      if x == dest_x:
        break
      error = error + dy
      x = x + sx
    if move_y:
      if move_x and contiguous:
        yield (x, y)
      if y == dest_y:
        break
      error = error + dx
      y = y + sy
  yield (dest_x, dest_y)

def offset(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
  return (p1[0] + p2[0], p1[1] + p2[1])

# (1, 2) -> (-2, 1) -> (-1, -2) -> (2, -1) -> ...
def rotate_right(x: int, y: int) -> Tuple[int, int]:
  return (-y, x)

# (1, 2) -> (2, -1) -> (-1, -2) -> (-2, 1) -> ...
def rotate_left(x: int, y: int) -> Tuple[int, int]:
  return (y, -x)

# (1, 2) -> (-1, -2) -> ...
def rotate_180(x: int, y: int) -> Tuple[int, int]:
  return (-x, -y)