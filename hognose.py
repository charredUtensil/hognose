#!/usr/bin/python3

import argparse
import os.path
import sys
import traceback
import time

from lib import Cavern
from lib.base import Context
from lib.version import VERSION_INFO, VERSION

__version_info__ = VERSION_INFO
__version__ = VERSION

def main():
  parser = argparse.ArgumentParser(
    prog=f'hognose',
    description='Procedurally generates caverns for Manic Miners.',
    usage='hognose [-d] [-o FILENAME] [-s SEED]'
  )
  parser.add_argument(
    '-d', '--draw',
    action=argparse.BooleanOptionalAction,
    help='Draw the cavern generation process to the screen.')
  parser.add_argument(
    '-o', '--out',
    help=(
      'Write file to OUT (- for stdout). If OUT is a directory, a filename '
      'will be generated.'))
  parser.add_argument(
    '-s', '--seed',
    help='Use SEED for cavern generation.')
  parser.add_argument(
    '-v', '--version',
    action='version',
    version=VERSION)

  args = parser.parse_args()
  if args.draw is None and args.out is None:
    parser.error(
        'Nothing to do. Specify -d to draw cavern or -o to output to file.')

  inx = None
  if args.draw:
    from inspector import Inspector
    inx = Inspector()

  context = Context(
    seed = args.seed,
    logger = inx)
  cavern = Cavern(context)
  if inx:
    inx.cavern = cavern

  start_time = time.time_ns()
  try:
    cavern.generate()
  except Exception as e:
    print(
        f'Failed to generate cave {hex(context.seed)}',
        file=sys.stderr)
    sys.exit(1)
  if args.out == '-':
    print(cavern.serialized)
  elif args.out:
    filename = args.out
    if os.path.isdir(filename):
      filename = os.path.join(filename, f'{cavern.diorama.level_name}.dat')
    with open(filename, 'w') as f:
      f.write(cavern.serialized)
  print((
    f'Generated {cavern.diorama.level_name} with seed {hex(context.seed)} '
    f'in {(time.time_ns() - start_time) // 1_000_000}ms'),
    file=sys.stderr)
  if inx:
    inx.wait()

if __name__ == '__main__':
  main()