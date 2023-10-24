class OnionFactoryBuilder(object):

  def __init__(self):
    self._stops = []

  def w(self, min_thickness, max_thickness, tile):
    self._stops.append((min_thickness, max_thickness, tile))
    return self

  def build(self):
    return OnionFactory(self._stops)

class OnionFactory(object):

  def __init__(self, stops):
    self._stops = tuple(stops)

  def create(self, context, id):
    def stops():
      total_thickness = 0
      for min_thickness, max_thickness, tile in self._stops:
        total_thickness += min_thickness + context.rng(id).random() * (max_thickness - min_thickness)
        yield total_thickness, tile
    s = tuple(stops())
    t = sum(th for th, _ in s)
    return Onion((th / t, ti) for (th, ti) in s)

class Onion(object):

  def __init__(self, stops):
    self._stops = tuple(stops)

  def stops(self):
    return self._stops