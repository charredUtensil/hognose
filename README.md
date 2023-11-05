[Hognose](https://en.wikipedia.org/wiki/Hognose)
is a procedural map generator for
[Manic Miners](https://manicminers.baraklava.com/)

# Running

As of now, this is still a bit crude:
- Install Python 3
- Edit values in context.py, if you want
- `./hognose -d -o out/demo.dat`
- You will see a Pygame window with a preview of the level
- The level will be saved to out/demo.dat
- Copy this to your Manic Miners installation to play the level

Future updates will introduce a better CLI

# Contributing

I'm hanging out on the Manic Miners discord. Ping me if you're interested in
contributing to avoid duplicate work.

This project uses type signatures from PyType. Please run `pytype .` on this
project before submitting a pull request. I'll figure out pip and precommit
hooks eventually, but this is the first time I've set up a Git project from
scratch in a while. Feel free to send a PR that fixes this.

# FAQ

## Why?

Rock Raiders is a rather unique game from 1999. It plays kind of like an RTS,
but with a heavy focus on economy and logistics. I enjoyed it tremendously as
a kid and I'm enjoying Baraklava's remake now. I've also always been fascinated
by algorithmically generated content. Many RTS games have some kind of random
map generator. I dabbled with scripting one in Age of Empires 2 a very long
time ago, but didn't get far. I've also loved every game I played that came
with a level editor, from
[Logic Quest 3D](https://www.youtube.com/watch?v=605CeYpos1U&list=PL7A1EE48A7DD84B65&ab_channel=maxmouse713)
to [Portal](https://www.moddb.com/mods/gamma-energy).

After playing with the level editor in Manic Miners a few times, I realized I
had a few interesting ideas for set pieces but not what to do with the rest of
the cavern.

I've had a lot of fun with this mainly because it's using an approach that
would be feasible back in 1999, and I feel like that's appropriate.

## Can I use this as a template to build my custom Manic Miners level on?

Sure! I'd just appreciate a callout if you do.

## Can Hognose make a level that...

Add an issue and maybe!

## Were any of these Qs actually FA'ed?

No.