This package generates text shown at the beginning and end of the level.

It does so through the use of _premise graphs_.

# Graphs

## Premise
![premises](/lib/lore/premises.svg)

## Orders
![orders](/lib/lore/orders.svg)

## Success
![success](/lib/lore/success.svg)

## Failure
![failure](/lib/lore/failure.svg)

# Syntax

Initialize the premise graph with `pg = PhraseGraph()`.

`a = pg('one', 'two' 'three')` creates a Phrase that randomly selects between one of the three texts given.
Phrases are linked with the `>>` operator. `a >> b` allows `b` to come after `a`.
Phrases are merged with the `|` operator. `c >> (a | b) >> d` allows either `a` or `b` to come after `c` and before `d`.
The `>>` operator also accepts a string or tuple of strings, as a shorthand: `a >> '.' >> b`, `a >> ('and', 'then') >> b`
Conditional state checkpoints ensure only relevant text is shown for a cavern. `a & 'has_monsters'` adds a checkpoint with the `has_monsters` state.

When generating text, the `PhraseGenerator` accepts a set of states. It will choose a path that goes through each passed state exactly once, and each state not passed exactly zero times.
Spaces will be added automatically before Phrases that do not start with punctuation.