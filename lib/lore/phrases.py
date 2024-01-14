from typing import FrozenSet, Iterable, List, Tuple

import functools

class Phrase(object):

  def __init__(self, id: int, texts: Iterable[str]):
    self._id = id
    self._texts = tuple(texts)
    self._after = []
    self._before = []

  def __str__(self):
    return f'{self._id}\n'+'\n\n'.join(_word_wrap(t, 40) for t in self._texts)

  def __repr__(self):
    return f'{self._id}[%s]' % '/'.join(t[:10] for t in self._texts)

  def _join(self, other: 'Phrase'):
    self._after.append(other._id)
    other._before.append(self._id)

class Condition(Phrase):

  def __init__(self, id: int, state):
    super().__init__(id, [])
    self.state = state

  def __str__(self):
    return f'{self._id}\n[{self.state}]'

class PhraseGraph(object):

  def __init__(self):
    self._phrases = []
    self._states = set()
    s = (self._condition('start'),)
    self.start = PgBuilder(self, s, s)
    self._end = self._condition('end')
    self.end = PgBuilder(self, (self._end,), (self._end,))

  def __call__(self, *args) -> 'PgBuilder':
    ph = (self._phrase(*args),)
    return PgBuilder(self, ph, ph)

  def _condition(self, state) -> Condition:
    self._states.add(state)
    r = Condition(len(self._phrases), state)
    self._phrases.append(r)
    return r

  def _phrase(self, *texts) -> Phrase:
    r = Phrase(len(self._phrases), texts)
    self._phrases.append(r)
    return r

  def dump_svg(self, filename: str):
    import pydot
    dot = pydot.Dot(graph_type='digraph', rankdir='LR')
    def mknode(p):
      n = pydot.Node(
          str(p),
          shape='rectangle' if p._texts else 'none',
          fontcolor='blue' if isinstance(p, Condition) else 'black')
      return n
    nodes = [mknode(p) for p in self._phrases]
    for n in nodes:
      dot.add_node(n)
    def edges():
      for p in self._phrases:
        for ida in p._after:
          pa = self._phrases[ida]
          is_condition = isinstance(p, Condition) or isinstance(pa, Condition)
          yield pydot.Edge(
              nodes[p._id],
              nodes[ida],
              color='blue' if is_condition else 'black')
    for e in edges():
      dot.add_edge(e)
    dot.write_svg(filename)

  def generate(self, rng, states):
    states = dict(states)
    states['start'] = True
    states['end'] = True
    self._check_state_keys(states)

    # Determine which sets of states can be reached at or downstream from each phrase
    tags: List[Optional[FrozenSet[FrozenSet[str]]]] = [None for p in self._phrases]
    tag_queue = set((self._end._id,))
    while tag_queue:
      id = tag_queue.pop()
      p = self._phrases[id]
      def pat():
        for ida in p._after:
          yield from tags[ida]
      pt = set(pat())
      # If we reach a condition...
      if isinstance(p, Condition):
        # ...for a state we want...
        if states[p.state]:
          # ...add it to all possible states and prune any downstream that already has
          # that state.
          pt.add(frozenset())
          ptc = frozenset((p.state,))
          pt = (s | ptc for s in pt if p.state not in s)
        # ...for a state we can't have
        else:
          # no possible states can be reached from here.
          # since 'end' is a state, that will ensure this path is not chosen.
          pt = frozenset()
      tags[id] = frozenset(pt)
      for idb in p._before:
        pb = self._phrases[idb]
        if not any(tags[idab] is None for idab in pb._after):
          tag_queue.add(idb)

    # Choose random path (n.b. this should probably be weighted instead)
    def walk():
      states_remaining = set(s for s, v in states.items() if v)
      p = self._phrases[0]
      cap = False
      while p != self._end:
        yield p
        if isinstance(p, Condition) and states[p.state]:
          states_remaining.remove(p.state)
        def c():
          for ida in p._after:
            for ta in tags[ida]:
              if states_remaining <= ta:
                yield ida
                break
        choices = tuple(c())
        if not choices:
          raise ValueError(
              f'No continuation has {repr(states_remaining)} at phrase #{p._id}')
        p = self._phrases[rng.uniform_choice(choices)]
    def join():
      capitalize_next = True
      for p in walk():
        if p._texts:
          text = rng.uniform_choice(p._texts)
          if capitalize_next:
            text = text[0].upper() + text[1:]
          if text[0] not in frozenset(',.!?'):
            yield ' '
          capitalize_next = text[-1] in frozenset('.!?')
          yield text
    return ''.join(join())

  def _check_state_keys(self, state):
    passed = set(state)
    u = passed.difference(self._states)
    if u:
      raise ValueError(f'{repr(u)} in args but not in the graph')
    m = self._states.difference(passed)
    if m:
      raise ValueError(f'{repr(m)} in graph but missing from args')

class PgBuilder(object):

  def __init__(
      self,
      pg: PhraseGraph,
      heads: Tuple[Phrase],
      tails: Tuple[Phrase]):
    self._pg = pg
    self._heads = heads
    self._tails = tails
    
  def __or__(self, other: 'PgBuilder') -> 'PgBuilder':
    return PgBuilder(
        self._pg,
        self._heads + other._heads,
        self._tails + other._tails)

  def __repr__(self):
    return f'PgBuilder {repr(self._heads)}>>{repr(self._tails)}'

  def __and__(self, state) -> 'PgBuilder':
    ph = self._pg._condition(state)
    for t in self._tails:
      t._join(ph)
    return PgBuilder(self._pg, self._heads, (ph,))

  def __rshift__(self, other) -> 'PgBuilder':
    if isinstance(other, PgBuilder):
      for t in self._tails:
        for h in other._heads:
          t._join(h)
      return PgBuilder(self._pg, self._heads, other._tails)
    else:
      ph = (self._pg._phrase(other) if isinstance(other, str)
          else self._pg._phrase(*other))
      for t in self._tails:
        t._join(ph)
      return PgBuilder(self._pg, self._heads, (ph,))


def _word_wrap(text: str, chars: int):
  def h():
    for line in text.splitlines():
      while line:
        if len(line) <= chars:
          yield line
          break
        ptr = chars
        while ptr > 0:
          if line[ptr].isspace():
            yield line[:ptr]
            line = line[ptr+1:]
            break
          ptr -= 1
        else:
          yield line[:chars]
          line = line[chars:]
  return '\n'.join(h())