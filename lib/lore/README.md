This package generates text shown at the beginning and end of the level.

It does so through the use of `PhraseGraph`s.

When generating text, the `PhraseGraph` accepts a set of states.
It will choose a path that goes from `start` to `end` through each passed state exactly once,
and each state not passed exactly zero times.
Spaces will be added automatically before Phrases that do not start with punctuation.

# Graphs

## Premise
![premises](/lib/lore/premises.svg)

## Orders
![orders](/lib/lore/orders.svg)

## Success
![success](/lib/lore/success.svg)

## Failure
![failure](/lib/lore/failure.svg)

## Found Hoard (event)
![found_hoard](/lib/lore/found_hoard.svg)

## Found HQ (event)
![found_hq](/lib/lore/found_hq.svg)

## Found Lost Miners (event)
(This only triggers if there are still more miners to find)
![found_lost_miners](/lib/lore/found_lost_miners.svg)

## Found All Lost Miners (event)
![found_all_lost_miners](/lib/lore/found_all_lost_miners.svg)

# Syntax

Initialize the premise graph with `pg = PhraseGraph()`.

## Phrases

`a = pg('one', 'two' 'three')` creates a Phrase that randomly selects between one of the three texts given.

## Phrase Chains

Phrases are linked sequentially with the `>>` operator. `a >> b` allows `b` to come after `a`.

Phrases are merged with the `|` operator. `c >> (a | b) >> d` allows either `a` or `b` to come after `c` and before `d`.

The `~` operator causes a phrase chain to be bypassable. That is, `a >> ~b >> c` is equivalent to `a >> b >> c` and `a >> c`

When using operators, you can usually use a string or tuple as a shorthand as long as there is another phrase in the chain. For example, `a >> '.' >> b`, `a >> ('and', 'then') >> b`

## Conditional States

Conditional state checkpoints ensure only relevant text is shown for a cavern.

Create a checkpoint on the state `'one'` with `pg('one')`. `pg.states('one', 'two', 'three')` is equivalent to `pg.states('one') | pg.states('two') | pg.states('three')`

The `&` operator is a shorthand: `a & 'has_monsters'` is equivalent to `a >> pg.states('has_monsters')`: it adds a single checkpoint with the `has_monsters` state.

## Special Phrases

The `PhraseGraph` includes the phrases `pg.start` and `pg.end`.
When generating text, the graph always starts at `start` and ends at `end`.
There should be no dead ends or cycles in the graph.

There is also a special phrase `pg.void` that can be used to halt chains.
It is most useful within complex single-line chains.
For example, `a >> (b >> pg.void | c | pg.void >> d) >> e` is equivalent to
`a >> b`, `a >> c >> e`, and `d >> e`.
Note the link is not formed between `b` and `d`.