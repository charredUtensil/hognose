#!/usr/bin/python3

import argparse
import sys
import unittest

from tests import *
from tests.base import SerializedCavernTest

def main():
  parser = argparse.ArgumentParser(
    prog=f'test',
    description='Run and update tests.',
    usage='test [-u]'
  )
  parser.add_argument(
    '-d', '--draw-generation',
    action=argparse.BooleanOptionalAction,
    help='Draw caverns being generated.'
  )
  parser.add_argument(
    '-u', '--update-resources',
    action=argparse.BooleanOptionalAction,
    help='Update test resources to match results.'
  )

  args, unknown = parser.parse_known_args()
  if args.update_resources:
    SerializedCavernTest.update_resources

  unittest.main(argv=([sys.argv[0]] + unknown))

main()