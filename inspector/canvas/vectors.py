from typing import TYPE_CHECKING, Union

import abc
import enum

if TYPE_CHECKING:
  from inspector.canvas.draw_context import DrawContext


class BaseVector(abc.ABC):
  def __init__(self, scaled, absolute):
    self._scaled: float = scaled
    self._absolute: float = absolute

  @property
  def scaled(self):
    return self._scaled

  @property
  def absolute(self):
    return self._absolute

  @abc.abstractmethod
  def __add__(self, other):
    pass

  def __radd__(self, other):
    return self.__add__(other)

  def __repr__(self):
    return f'{type(self).__name__}: {self.scaled:.2f}, {self.absolute:.2f}'

  def tr(self, dc: 'DrawContext') -> float:
    return dc.scale * self.scaled + self.absolute


class FreeVector(BaseVector):

  def __add__(self, other):
    if isinstance(other, FreeVector):
      return FreeVector(
          self.scaled + other.scaled,
          self.absolute + other.absolute)
    if isinstance(other, (int, float)):
      return FreeVector(self.scaled + other, self.absolute)
    return NotImplemented

  def __sub__(self, other):
    if isinstance(other, (FreeVector, int, float)):
      return self + -1 * other
    return NotImplemented

  def __rsub__(self, other):
    if isinstance(other, (FreeVector, int, float)):
      return other + -1 * self
    return NotImplemented

  def __mul__(self, other):
    if isinstance(other, (int, float)):
      return FreeVector(self.scaled * other, self.absolute * other)
    return NotImplemented

  def __rmul__(self, other):
    return self.__mul__(other)

  def __truediv__(self, other):
    if isinstance(other, (int, float)):
      return FreeVector(self.scaled / other, self.absolute / other)
    return NotImplemented

  def __floordiv__(self, other):
    if isinstance(other, (int, float)):
      return FreeVector(self.scaled // other, self.absolute // other)
    return NotImplemented


class AnchoredVector(BaseVector):
  @abc.abstractmethod
  @property
  def anchor(self):
    pass

  def __sub__(self, other):
    if isinstance(other, FreeVector):
      return self + -1 * other
    return NotImplemented

  def __repr__(self):
    return f'{super().__repr__()}, {self.anchor}'

  def tr(self, dc) -> float:
    return super().tr(dc) + dc.anchors[self.anchor]


class XVector(AnchoredVector):

  class Anchor(enum.Enum):
    CENTER_X = enum.auto()
    ORIGIN_X = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()

  def __init__(self, scaled, absolute, anchor: 'XVector.Anchor'):
    super().__init__(scaled, absolute)
    self._anchor = anchor

  @property
  def anchor(self):
    return self._anchor

  def __add__(self, other):
    if isinstance(other, FreeVector):
      return XVector(
          self.scaled + other.scaled,
          self.absolute + other.absolute,
          self.anchor)
    if isinstance(other, (int, float)):
      return XVector(self.scaled + other, self.absolute, self.anchor)
    return NotImplemented


class YVector(AnchoredVector):

  class Anchor(enum.Enum):
    CENTER_Y = enum.auto()
    ORIGIN_Y = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()

  def __init__(self, scaled, absolute, anchor: 'YVector.Anchor'):
    super().__init__(scaled, absolute)
    self._anchor = anchor

  @property
  def anchor(self):
    return self._anchor

  def __add__(self, other):
    if isinstance(other, FreeVector):
      return YVector(
          self.scaled + other.scaled,
          self.absolute + other.absolute,
          self.anchor)
    if isinstance(other, float):
      return YVector(self.scaled + other, self.absolute, self.anchor)
    return NotImplemented


def a(v: Union[FreeVector, float]):
  if isinstance(v, FreeVector):
    return v
  return FreeVector(0, v)


def s(v: Union[FreeVector, float]):
  if isinstance(v, FreeVector):
    return v
  return FreeVector(v, 0)


def x(v: Union[XVector, float]) -> XVector:
  if isinstance(v, XVector):
    return v
  return XVector(v, 0, XVector.Anchor.ORIGIN_X)


def y(v: Union[YVector, float]) -> YVector:
  if isinstance(v, YVector):
    return v
  return YVector(v, 0, YVector.Anchor.ORIGIN_Y)


def xy(v):
  vx, vy = v
  return x(vx), y(vy)


def xywh(v):
  vx, vy, vw, vh = v
  return x(vx), y(vy), s(vw), s(vh)


CENTER_X = XVector(0, 0, XVector.Anchor.CENTER_X)
ORIGIN_X = XVector(0, 0, XVector.Anchor.ORIGIN_X)
LEFT = XVector(0, 0, XVector.Anchor.LEFT)
RIGHT = XVector(0, 0, XVector.Anchor.RIGHT)

CENTER_Y = YVector(0, 0, YVector.Anchor.CENTER_Y)
ORIGIN_Y = YVector(0, 0, YVector.Anchor.ORIGIN_Y)
TOP = YVector(0, 0, YVector.Anchor.TOP)
BOTTOM = YVector(0, 0, YVector.Anchor.BOTTOM)
