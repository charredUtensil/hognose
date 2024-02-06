[Hognose](https://en.wikipedia.org/wiki/Hognose)
is a procedural map generator for
[Manic Miners](https://manicminers.baraklava.com/)

# Running

## Setup

1. Install [Python](https://www.python.org/downloads/)
1. (Optional) Set up a venv
 2. `python -m venv .venv`
 2. `source .venv/bin/activate` (bash/zsh), `.venv\Scripts\activate.bat`
   (cmd.exe), or `.venv\Scripts\Activate.ps1` (PowerShell)
1. Install dependencies
 - `python -m pip install -r requirements.txt`
 - If you will be developing Hognose, use `requirements_dev.txt` instead

## Running

Run Hognose with `python hognose.py` for a list of flags.

Generate a random map and add it directly to the Manic Miners level folder:
`python hognose.py -o %HOMEDRIVE%%HOMEPATH%\Documents\ManicMiners\Levels`

## Troubleshooting

### I get a `ModuleNotFoundError`

You probably have more than one version of Python installed on your computer

# Contributing

I am on the Manic Miners discord. Ping me if you're interested in contributing
and I can offer advice and/or suggestions.

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
the cavern - and now here we are.

## Which AI does this use?

None. All of the caverns are procedurally generated using an approach that
would have been feasible back in 1999. Procedural generation means there are a
series of specific rules that determine where everything in the level gets
placed, and while there is some randomness within those rules, the rules
themselves are hand-crafted.

A modern "AI" would be somewhat unhelpful in this situation. There aren't
nearly enough Manic Miners levels in existence to train the AI on what makes a
level *winnable*, and the system requirements would far exceed Manic Miners
itself, even on max graphics settings.

## Can I use this as a template to build my custom Manic Miners level on?

Sure! I'd appreciate it if you included a link to this GitHub page.

## Can Hognose make a level that...

Add an issue and maybe! Generally speaking, the kind of things that would be
easier to add would be caves with specific things in them - like

## Can I tweak the level generation?

Sure! For now, most of the level parameters can be found in
lib/base/context.py, so editing that will change the resulting map. Due to the
way caverns are generated, this may result in changes to seemingly unrelated
parts of the cavern.

## Can you give me some cool seeds to play?

Unfortunately, things have been changing so quickly that seeds still aren't
generating consistent caverns between versions.

- 0x659f9b99 - Find a ruined base in a lava cavern
- 0x65a20857 - A large water lake in a lava cavern
- 0x65a72422 - A large lava lake in an ice cavern
- 0x65aa0e8b - Somewhat balanced level where erosion is a problem
  a.k.a. (Snake of Fire)
- 0x65b48a5f - All possible objective types at the same time
- 0x65b99260 - Ruined Base Spawn

## Were any of these Qs actually FA'ed?

No.