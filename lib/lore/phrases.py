from typing import Dict, FrozenSet, Iterable, List, Set, Tuple

import collections
import functools

class Phrase(object):

  def __init__(self, id: int, texts):
    self._id: int = id
    self._texts: Tuple[str] = tuple(texts)
    self._after: List['Phrase'] = []
    self._before: List['Phrase'] = []
    self._tagged_states: Optional[Dict(FrozenSet[str], int)] = None

  def __str__(self):
    return f'{self._id}\n'+'\n'.join(_word_wrap(t, 40) for t in self._texts)

  def __repr__(self):
    return f'{self._id}[%s]' % '/'.join(t[:10] for t in self._texts)

  def _join(self, other: 'Phrase'):
    self._after.append(other)
    other._before.append(self)

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
    dot = pydot.Dot(graph_type='digraph', rankdir='LR', TBbalance='max')
    def mknode(p):
      n = pydot.Node(
          str(p),
          shape='rectangle' if p._texts else 'none',
          fontcolor=_graph_node_color(p))
      return n
    nodes = [mknode(p) for p in self._phrases]
    for n in nodes:
      dot.add_node(n)
    def edges():
      for p in self._phrases:
        for after in p._after:
          yield pydot.Edge(
              nodes[p._id],
              nodes[after._id],
              color=_graph_edge_color(p, after))
    for e in edges():
      dot.add_edge(e)
    dot.write_svg(filename)
  
  def compile(self):
    # Determine which sets of states can be reached at or downstream from each phrase
    queue: Set[Phrase] = set(p for p in self._phrases if not p._after)
    while queue:
      p = queue.pop()
      pt = collections.Counter()
      for after in p._after:
        for states, count in after._tagged_states.items():
          pt[states] += count
      # If we reach a condition...
      if isinstance(p, Condition):
        # ...add it to all possible states and prune any downstream that already has
        # that state.
        ptc = frozenset((p.state,))
        pt2 = {} if pt else {ptc: 1}
        for states, count in pt.items():
          if p.state not in states:
            pt2[states | ptc] = count + 1
        p._tagged_states = pt2
      else:
        p._tagged_states = pt
      for pb in p._before:
        if not any(pab._tagged_states is None for pab in pb._after):
          queue.add(pb)

  def generate(self, rng, states: FrozenSet[str]):
    states = (states & self._states) | frozenset(('start', 'end'))

    def walk():
      states_remaining = frozenset(states)
      p = self._phrases[0]
      while p != self._end:
        if p._texts:
          yield rng.uniform_choice(p._texts)
        if isinstance(p, Condition):
          states_remaining -= frozenset((p.state,))
        choices = tuple(
            after for after in p._after
            if states_remaining in after._tagged_states)
        if not choices:
          continuations = ''.join(
              f'\n  {after._id:2d}:' + ''.join(
                  f'\n    {repr(ts)}' for ts in after._tagged_states)
              for after in p._after)
          raise ValueError(
              f'No continuation has {repr(states_remaining)} '
              f'at phrase #{p._id}.\n'
              f'Continuations:{continuations}')
        p = rng.uniform_choice(choices)

    return ''.join(_join_phrase_texts(walk()))

class PgBuilder(object):

  def __init__(
      self,
      pg: PhraseGraph,
      heads: Tuple[Phrase],
      tails: Tuple[Phrase]):
    self._pg = pg
    self._heads = heads
    self._tails = tails

  def __repr__(self):
    return f'PgBuilder {repr(self._heads)}>>{repr(self._tails)}'

  def __and__(self, state) -> 'PgBuilder':
    ph = self._pg._condition(state)
    for t in self._tails:
      t._join(ph)
    return PgBuilder(self._pg, self._heads, (ph,))
    
  def __or__(self, other: 'PgBuilder') -> 'PgBuilder':
    return PgBuilder(
        self._pg,
        self._heads + other._heads,
        self._tails + other._tails)

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

def _graph_node_color(p):
  if not any('end' in ts for ts in (p._tagged_states or ())):
    return 'red'
  if isinstance(p, Condition):
    return 'blue'
  return 'black'

def _graph_edge_color(p1, p2):
  if not any('end' in ts for ts in (p2._tagged_states or ())):
    return 'red'
  if isinstance(p1, Condition) or isinstance(p2, Condition):
    return 'blue'
  return 'black'

def _join_phrase_texts(texts):
  capitalize_next = True
  for i, text in enumerate(texts):
    if i > 0 and text[0] not in frozenset(',.!?\n'):
      yield ' '
    if capitalize_next:
      yield text[0].upper()
      yield text[1:]
    else:
      yield text
    capitalize_next = text[-1] in frozenset('.!?')

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