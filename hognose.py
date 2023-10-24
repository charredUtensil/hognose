#!/usr/bin/python3

import argparse

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
    parser.error('Nothing to do. Specify -d to draw cavern or -o to output to file.')

  inx = None
  if args.draw:
    from inspector import Inspector
    inx = Inspector()

  cavern = Cavern(Context(seed=args.seed))
  for stage, item in cavern.generate():
    if inx:
      inx.draw(cavern, stage, item)
  serialized = cavern.serialize()
  if args.out == '-':
    print(serialized)
  elif args.out:
    with open(args.out, 'w') as f:
      f.write(serialized)
  if inx:
    inx.wait()

if __name__ == '__main__':
  main()