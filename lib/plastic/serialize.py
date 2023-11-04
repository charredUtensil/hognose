from typing import Dict, Iterable, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
  from .diorama import Diorama

T = TypeVar('T')

from .position import Position
from .tile import Tile
from lib.version import VERSION

def serialize(diorama: 'Diorama') -> str:
  return '\n'.join(_serialize(diorama))

def _serialize(diorama: 'Diorama') -> Iterable[str]:
  left, top, width, height = diorama.bounds
  eox = width // 2
  eoy = height // 2

  yield 'comments{'
  for c in _comments(diorama):
    yield f'  {c}'
  yield '}'

  yield 'info{'
  yield f'rowcount:{width:d}'
  yield f'colcount:{height:d}'
  yield f'camerapos:{_camera_origin(diorama)}'
  yield 'biome:rock'
  yield 'creator:hognose'
  yield 'spiderrate:10'
  yield 'spidermin:2'
  yield 'spidermax:4'
  yield 'version:2023-08-14-1'
  yield f'opencaves:{_tile_coords(diorama, sorted(diorama.open_cave_flags))}'
  yield '}'

  yield 'tiles{'
  yield from _tile_grid(
    diorama,
    Tile.SOLID_ROCK.export_value,
    dict(_tile_export_values(diorama)))
  yield '}'

  yield 'height{'
  for _ in range(height + 1):
    yield ''.join('0,' * (width + 1))
  yield '}'

  yield 'resources{'
  yield 'crystals:'
  yield from _tile_grid(diorama, 0, diorama.crystals)
  yield 'ore:'
  yield from _tile_grid(diorama, 0, diorama.ore)
  yield '}'

  yield 'objectives{'
  for o in diorama.objectives:
    yield o.serialize()
  yield '}'

  yield 'buildings{'
  for b in diorama.buildings:
    yield b.serialize((-left, -top))
  yield '}'

  yield 'landslidefrequency{'
  yield '}'
  yield 'lavaspread{'
  yield '}'
  yield 'miners{'
  yield '}'

  yield 'briefing{'
  yield diorama.briefing
  yield '}'
  yield 'briefingsuccess{'
  yield diorama.briefing_success
  yield '}'
  yield 'briefingfailure{'
  yield diorama.briefing_failure
  yield '}'

  yield 'vehicles{'
  yield '}'
  yield 'creatures{'
  yield '}'
  yield 'blocks{'
  yield '}'
  yield 'script{'
  yield ''
  yield '}'

def _comments(diorama: 'Diorama') -> Iterable[str]:
  yield 'Cavern generated by Hognose'
  yield 'https://github.com/charredUtensil/hognose'
  yield f'version:{VERSION}'
  yield str(diorama.context)

def _camera_origin(diorama: 'Diorama') -> str:
  left, top, _, _ = diorama.bounds
  x, y = diorama.camera_origin
  return Position((x, y, 0), (45, 90, 0)).serialize((-left, -top))

def _tile_export_values(
    diorama: 'Diorama') -> Iterable[Tuple[Tuple[int, int], int]]:
  for coord, tile in diorama.tiles.items():
    v = tile.export_value
    if not tile.is_wall and coord not in diorama._discovered:
      v += 100
    yield coord, v

def _tile_grid(
    diorama: 'Diorama',
    default: T,
    grid: Dict[Tuple[int, int], T]) -> Iterable[str]:
  left, top, width, height = diorama.bounds
  for y in range(top, top + height):
    yield ''.join(
      f'{grid.get((x, y), default)},'
      for x in range(left, left + width))

def _tile_coords(
    diorama: 'Diorama',
    coords: Iterable[Tuple[int, int]]) -> str:
  left, top, _, _ = diorama.bounds
  return ''.join(f'{y - top :d},{x - left :d}/' for x, y in coords)