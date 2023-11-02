from typing import Dict, Tuple

from lib.base import SoftLockedError
from lib.plastic import Diorama, Building, Tile

def patch(tiles: Dict[Tuple[int, int], Tile]):
  left   = min(x for x, y in tiles)
  right  = max(x for x, y in tiles)
  top    = min(y for x, y in tiles)
  bottom = max(y for x, y in tiles)
  for x in range(left, right + 1):
    for y in range(top, bottom + 1):
      if not tiles.get((x, y), Tile.SOLID_ROCK).is_wall:
        continue
      neighbors = tuple(
          ((ox, oy), tiles.get((x + ox, y + oy), Tile.SOLID_ROCK))
          for (ox, oy)
          in ((0, -1), (0, 1), (-1, 0), (1, 0)))
      wall_neighbors = tuple(
          (ox, oy)
          for (ox, oy), tile
          in neighbors
          if tile.is_wall)
      if len(wall_neighbors) > 1:
        continue
      if not wall_neighbors:
        wall_neighbors = ((0, -1),)
        tiles[x, y - 1] = Tile.DIRT
      ox, oy = wall_neighbors[0]
      # Right turn
      tiles[x - oy, y + ox] = Tile.DIRT
      # Remaining square
      if not tiles.get((x + ox - oy, y + ox + oy), Tile.SOLID_ROCK).is_wall:
        tiles[x + ox - oy, y + ox + oy] = Tile.DIRT
      
def playtest(diorama: Diorama):
  ore = 0
  crystals = 0
  buildable = 0
  visited = {}
  queues: Dict[Tile, List[Tuple[int, int]]] = {
    Tile.FLOOR: [],
    Tile.LAVA: [],
    Tile.WATER: [],
    Tile.FOUNDATION: [],
    Tile.POWER_PATH: [],
    Tile.DIRT: [],
    Tile.LOOSE_ROCK: [],
    Tile.HARD_ROCK: [],
    Tile.CRYSTAL_SEAM: [],
    Tile.ORE_SEAM: [],
  }
  for b in diorama.buildings:
    if b.type == Building.TOOL_STORE:
      if (b.x, b.y) in diorama.discovered:
        tile = diorama.tiles[b.x, b.y]
        queues[tile].append((b.x, b.y))
  if all(not q for q in queues.values()):
    raise SoftLockedError('Can\'t determine starting position.')

  def _can_build_tunnel_scout():
    return (
        crystals >= (0
            + 2 # Power Station
            + 1 # Power for Teleport Pad
            + 3 # Tunnel Scout
        )
        and
        ore >= (0
            + 8 # Teleport Pad
            +10 # Power Station
        )
        and
        buildable >= (0
            + 2 # Tool Store
            + 2 # Teleport Pad
            + 3 # Power Station
            + 2 # Support Station
        )
    )

  def _can_build_rapid_rider():
    return (
        crystals >= (0
            + 2 # Power Station
            + 1 # Docks
            + 1 # Power for Docks
            + 2 # Teleport Rapid Rider
        )
        and
        ore >= (0
            + 8 # Teleport Pad
            +10 # Power Station
            + 8 # Docks
        )
        and
        buildable >= (0
            + 2 # Tool Store
            + 2 # Teleport Pad
            + 3 # Power Station
            + 2 # Docks
        )
    )

  def _pop() -> Tuple[int, int]:
    nonlocal queues, ore, crystals, buildable

    # Tiles that one miner can always traverse
    for tile, bonus_ore, bonus_crystals in (
        (Tile.FOUNDATION,   0, 0),
        (Tile.POWER_PATH,   0, 0),
        (Tile.FLOOR,        0, 0),
        (Tile.CRYSTAL_SEAM, 4, 4),
        (Tile.DIRT,         4, 0),
        (Tile.LOOSE_ROCK,   4, 0),
        (Tile.ORE_SEAM,     8, 0)):
      if queues[tile]:
        ore += bonus_ore
        crystals += bonus_crystals
        buildable += 1
        return queues[tile].pop(0)
    # Tiles reachable by vehicles
    if _can_build_tunnel_scout():
      for tile in (Tile.WATER, Tile.LAVA):
        if queues[tile]:
          return queues[tile].pop(0)
    elif _can_build_rapid_rider():
      if queues[Tile.WATER]:
        return queues[Tile.WATER].pop(0)
    # If the player has 10 ore, assume they can at least use dynamite
    if ore >= 10:
      if queues[Tile.HARD_ROCK]:
        ore += 4
        return queues[Tile.HARD_ROCK].pop(0)
    return None

  while True:
    coord = _pop()
    if coord:
      print(f'{repr(coord)} {diorama.tiles[coord].export_value}')
      ore += diorama.ore.get(coord, 0)
      crystals += diorama.crystals.get(coord, 0)
      if crystals >= 25:
        break
      visited[coord] = None
      for ox, oy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        next_coord = coord[0] + ox, coord[1] + oy
        if next_coord not in visited:
          tile = diorama.tiles.get(next_coord, Tile.SOLID_ROCK)
          if tile in queues:
            q = queues[tile]
            if next_coord not in q:
              q.append(next_coord)
      continue
    if crystals < 6 and (queues[Tile.WATER] or queues[Tile.LAVA]):
      placement = None
      for coord in visited:
        tile = diorama.tiles[coord]
        if tile in (
            Tile.DIRT, Tile.LOOSE_ROCK, Tile.CRYSTAL_SEAM):
          placement = coord
        elif tile == Tile.HARD_ROCK:
          break
      if placement:
        diorama.crystals[placement] += (6 - crystals)
        crystals = 6
        continue
    if ore < 10 and queues[Tile.HARD_ROCK]:
      placement = None
      for coord in visited:
        tile = diorama.tiles[coord]
        if tile in (Tile.DIRT, Tile.LOOSE_ROCK):
          placement = coord
        elif tile == Tile.HARD_ROCK:
          break
      if placement:
        diorama.tiles[placement] = Tile.ORE_SEAM
        diorama.ore[placement] += (10 - 4 - ore)
        ore = 10
        continue
    raise SoftLockedError(
        f'Can\'t escape island start with {ore} ore and {crystals} crystals.')
