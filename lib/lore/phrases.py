from typing import Dict, FrozenSet, List, Optional, Set, Tuple, Union

import collections

from lib.utils.text import word_wrap

# pylint: disable=protected-access

class Phrase():

  def __init__(self, id: int, texts):
    self._id: int = id
    self._texts: Tuple[str] = tuple(texts)
    self._after: List['Phrase'] = []
    self._before: List['Phrase'] = []
    self._tagged_states: Optional[Dict[FrozenSet[str], int]] = None
    self._is_reachable = False

  @property
  def _can_reach_end(self):
    return any('end' in ts for ts in (self._tagged_states or ()))

  def __str__(self):
    return f'{self._id}\n' + \
      '\n'.join(word_wrap(t.replace('\n', '\u2424'), 40) for t in self._texts)

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


class PhraseGraph():

  def __init__(self):
    self._phrases = []
    self._states = set()
    self._start = self._condition('start')
    self.start = PgBuilder(self, (), (self._start,))
    self._end = self._condition('end')
    self.end = PgBuilder(self, (self._end,), ())
    self.void = PgBuilder(self, (), ())

  def __call__(self, *args) -> 'PgBuilder':
    ph = (self._phrase(*args),)
    return PgBuilder(self, ph, ph)

  def states(self, *states) -> 'PgBuilder':
    ph = tuple(
        self._condition(s) if s else self._phrase() for s in states)
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
    import pydot # pylint: disable=import-outside-toplevel
    dot = pydot.Dot(graph_type='digraph', rankdir='LR')

    def mknode(p):
      n = pydot.Node(str(p), **_graph_node_attrs(p))
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
              **_graph_edge_attrs(p, after))
    for e in edges():
      dot.add_edge(e)
    dot.write_svg(filename) # pylint: disable=no-member

  def compile(self):
    # Determine which sets of states can be reached at or downstream from each
    # phrase
    queue: Set[Phrase] = set(p for p in self._phrases if not p._after)
    while queue:
      p = queue.pop()
      pt = collections.Counter()
      for after in p._after:
        for states, count in after._tagged_states.items():
          pt[states] += count
      # If we reach a condition...
      if isinstance(p, Condition):
        # ...add it to all possible states and prune any downstream that
        # already has that state.
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

    queue.add(self._phrases[0])
    while queue:
      p = queue.pop()
      p._is_reachable = True
      for after in p._after:
        if after not in queue and not after._is_reachable:
          queue.add(after)

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


class PgBuilder():

  def __init__(
      self,
      pg: PhraseGraph,
      heads: Tuple[Phrase, ...],
      tails: Tuple[Phrase, ...],
      bypass: bool = False):
    self._pg = pg
    self._heads = heads
    self._tails = tails
    self._bypass = bypass

  def __repr__(self):
    def j(ids):
      if len(ids) == 1:
        return str(ids[0])
      return f'({"|".join(str(id) for id in ids)})'
    return (
        'PgBuilder '
        f'{"~(" if self._bypass else ""}'
        f'{j(self._heads)}>>{j(self._tails)}'
        f'{")" if self._bypass else ""}')

  def _coerce(
      self, other: Union[str, Tuple[str, ...], 'PgBuilder']) -> 'PgBuilder':
    if isinstance(other, PgBuilder):
      return other
    ph = ((self._pg._phrase(other) if isinstance(other, str)
        else self._pg._phrase(*other)),)
    return PgBuilder(self._pg, ph, ph)

  def __and__(self, state: str) -> 'PgBuilder':
    ph = self._pg._condition(state)
    for t in self._tails:
      t._join(ph)
    return PgBuilder(self._pg, self._heads, (ph,))

  def __or__(self, other) -> 'PgBuilder':
    other = self._coerce(other)
    return PgBuilder(
        self._pg,
        tuple(set(self._heads + other._heads)),
        tuple(set(self._tails + other._tails)),
        self._bypass or other._bypass)

  def __ror__(self, other) -> 'PgBuilder':
    return self._coerce(other) | self

  def __invert__(self) -> 'PgBuilder':
    return PgBuilder(self._pg, self._heads, self._tails, bypass=True)

  def __rshift__(self, other) -> 'PgBuilder':
    other = self._coerce(other)
    for t in self._tails:
      for h in other._heads:
        t._join(h)
    return PgBuilder(
        self._pg,
        self._heads + other._heads if self._bypass else self._heads,
        self._tails + other._tails if other._bypass else other._tails,
        self._bypass and other._bypass)

  def __rrshift__(self, other) -> 'PgBuilder':
    return self._coerce(other) >> self


def _graph_node_attrs(p):

  if not (p._is_reachable and p._can_reach_end):
    return {
        'color': 'red',
        'fontcolor': 'red',
        'shape': 'rectangle',
        'style': 'dotted'}
  if p._id <= 1:
    return {'fontcolor': 'green', 'color': 'green', 'shape': 'circle'}
  if isinstance(p, Condition):
    return {'fontcolor': 'blue', 'shape': 'none'}
  if not p._texts:
    return {'shape': 'none'}
  return {'shape': 'rectangle'}


def _graph_edge_attrs(p1, p2):
  if not (p2._is_reachable and p2._can_reach_end):
    return {'color': 'red', 'style': 'dotted'}
  if p1._id <= 1 or p2._id <= 1:
    return {'color': 'green', 'style': 'dashed'}
  if isinstance(p1, Condition) or isinstance(p2, Condition):
    return {'color': 'blue'}
  return {}


def _join_phrase_texts(texts):
  capitalize_next = True
  space_next = False
  for text in texts:
    if space_next and text[0] not in frozenset(',.!?\n'):
      yield ' '
    if capitalize_next:
      yield text[0].upper()
      yield text[1:]
    else:
      yield text
    capitalize_next = text[-1] in frozenset('.!?\n')
    space_next = text[-1] not in frozenset('\n')
