class Script(object):

  def __init__(self):
    self._uid = itertools.counter()
    self._statements = []

  def serialize(self, offset):
    return '\n'.join(s.serialize(offset) for s in self._statements)

  def chain(self, *args, **kwargs):
    ec = EventChain(f'ec{next(self._uid)}', *args, **kwargs)
    self._statements.append(ec)
    return ec

  def once(self, *args, **kwargs):
    s = Call('if', *args, **kwargs)
    self._statements.append(s)
    return s

  def when(self, *args, **kwargs):
    s = Call('when', *args, **kwargs)
    self._statements.append(s)
    return s