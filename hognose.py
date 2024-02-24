#!/usr/bin/python3

import typing
from typing import List, Optional, TYPE_CHECKING

import argparse
import os.path
import re
import sys
import threading
import time

from lib import Cavern
from lib.base import (
    Context, GenerationError, Logger, MultiCavernLogger, MAX_SEED)
from lib.version import VERSION_INFO, VERSION

if TYPE_CHECKING:
  from inspector import Inspector

__version_info__ = VERSION_INFO
__version__ = VERSION


def _seeds(parser, args) -> List[int]:
  seed: Optional[str] = args.seed

  def parse(): # pylint: disable=inconsistent-return-statements
    # No seed: Use seconds since epoch
    if seed is None:
      return int(time.time()) % MAX_SEED

    # Seed that looks like a hex number: use that as seed
    m = re.match(
      r'\A\s*(0x)?'
      r'(?P<seed>[0-9a-fA-F]{1,8})'
      r'\s*\Z', seed)
    if m:
      r = int(m.group('seed'), 16)
      if r < MAX_SEED:
        return r

    # Seed that looks like a level name: extract seed
    m = re.match(
        r'\A\s*((HN-?)?[KEA])?'
        r'(?P<seed>[0-9a-fA-F]{3}-?[0-9a-fA-F]{5})'
        r'(\.dat)?'
        r'\s*\Z', seed)
    if m:
      r = int(m.group('seed').replace('-',''), 16)
      if r < MAX_SEED:
        return r

    parser.error(
      f'{repr(seed)} is not a valid seed. Seed must be either:\n'
      f'- A hexadecimal number between 0 and {MAX_SEED - 1:x}\n'
      '- A Hognose level name like HN-A199-91118')

  return [(parse() + i) % MAX_SEED for i in range(0, args.count)]


def main():
  parser = argparse.ArgumentParser(
    prog='hognose',
    description='Procedurally generates caverns for Manic Miners.',
    usage='hognose [FLAGS]')
  parser.add_argument(
    '-b', '--briefing',
    action=argparse.BooleanOptionalAction,
    help='Print the briefing after generating.')
  parser.add_argument(
    '-c', '--count',
    type=int,
    choices=range(1,9999),
    default=1,
    metavar='(1-9999)',
    help=(
        'How many caverns to generate. When generating multiple caverns, -o '
        'must be a directory.'))
  parser.add_argument(
    '-d', '--draw',
    action='append_const',
    const=1,
    help=(
        'Draw the cavern generation process to the screen. Repeat for more '
        'verbose drawing. This will cause caverns to generate slower.'))
  parser.add_argument(
    '-o', '--out',
    metavar='(-|FILE|DIR)',
    help=(
        'Where to write the file. Use - for stdout. If this is a directory, a '
        'filename will be generated from the level name.'))
  parser.add_argument(
    '-s', '--seed',
    help='Use SEED for cavern generation.')
  parser.add_argument(
    '-v', '--version',
    action='version',
    version=VERSION)

  args = parser.parse_args()
  if args.briefing is None and args.draw is None and args.out is None:
    parser.error(
        'Nothing to do. Specify -d to draw cavern or -o to output to file.')
  if args.briefing and args.out == '-':
    parser.error(
        'Stubbornly refusing to print both briefing and level.dat to stdout.')

  if args.count > 1:
    if (args.out is not None
        and (args.out == '-' or not os.path.isdir(args.out))):
      parser.error('-o must be a directory when generating multiple caverns.')

  seeds = _seeds(parser, args)

  inx: 'Optional[Inspector]' = None
  if args.draw:
    from inspector import Inspector # pylint: disable=import-outside-toplevel
    inx = Inspector(len(args.draw))
  logger: Logger = (inx or Logger())

  def graphics():
    if inx:
      typing.cast('Inspector', inx).run()
  graphics_thread = threading.Thread(target=graphics)
  graphics_thread.start()
  for i, seed in enumerate(seeds):
    context = Context.generate(
        seed=seed,
        logger=MultiCavernLogger(logger, i, len(seeds)))
    cavern = Cavern(context)
    start_time = time.time_ns()
    try:
      cavern.generate()
      if args.out == '-':
        print(cavern.serialized)
      elif args.out:
        filename = args.out
        if os.path.isdir(filename):
          filename = os.path.join(filename, f'{cavern.diorama.level_name}.dat')
        with open(filename, 'w', encoding='utf-8') as f:
          f.write(cavern.serialized)
      if args.briefing:
        print(cavern.diorama.briefing)
      print((
        f'Generated {cavern.diorama.level_name} with seed {hex(context.seed)} '
        f'in {(time.time_ns() - start_time) // 1_000_000}ms'),
        file=sys.stderr)
    except GenerationError:
      print(
          f'Failed to generate cave {hex(context.seed)}',
          file=sys.stderr)
  graphics_thread.join()


if __name__ == '__main__':
  main()
