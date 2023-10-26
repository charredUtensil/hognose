#!/usr/bin/python3

import argparse
import sys
import traceback

from inspector import Inspector
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
    help='Output file to write, or - for stdout.')
  parser.add_argument(
    '-s', '--seed',
    help='Main seed for cavern generation.')
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

  cavern = Cavern(Context(seed=args.seed))
  try:
    cavern.generate(logger=inx)
    serialized = cavern.serialize()
  except Exception as e:
    print(f'Exception on seed {hex(cavern.context.seed)}', file=sys.stderr)
    print(
        ''.join(traceback.format_exception(type(e), e, e.__traceback__)),
        file=sys.stderr)
    if inx:
      inx.log_exception(cavern, e)
      inx.wait()
    sys.exit(1)
  if args.out == '-':
    print(serialized)
  elif args.out:
    with open(args.out, 'w') as f:
      f.write(serialized)
  if inx:
    inx.wait()

if __name__ == '__main__':
  main()