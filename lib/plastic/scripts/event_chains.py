class EventChain(object):

  def __init__(self, name):
    self._name = name
    self._events = []

  def serialize(self, offset):
    return (
        f'{self._name}::;\n'
        f'{"\n".join(e.serialize(offset) for e in self._events)}\n\n')