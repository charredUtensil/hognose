#!/usr/bin/python3

import argparse
import sys
import unittest

from tests import *  # pylint: disable=wildcard-import, unused-wildcard-import
from tests.base import SerializedCavernTest


def main():
  parser = argparse.ArgumentParser(
    prog='test',
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
    SerializedCavernTest.update_resources = True

  unittest.main(argv=[sys.argv[0]] + unknown)


if __name__ == '__main__':
  main()
