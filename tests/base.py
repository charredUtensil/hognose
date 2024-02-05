import abc
import os.path
import re
import unittest

from lib.plastic import Diorama

RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')
SANITIZE_RE = re.compile(r'^comments{$.*?^}$', re.DOTALL | re.MULTILINE)


def sanitize(data: str) -> str:
  return SANITIZE_RE.sub('comments{\n[REDACTED]\n}', data)


class SerializedCavernTest(unittest.TestCase, abc.ABC):
  """A TestCase that tests serialized caverns."""

  def assertDioramaMatches(self, diorama: Diorama, resource: str): # pylint: disable=invalid-name
    """
    Asserts the given diorama serializes to the given resource.
    
    If update_resources is set to True, this updates the file instead.
    """
    filename = os.path.join(RESOURCE_DIR, f'{resource}.dat')
    actual = sanitize(diorama.serialize())
    try:
      with open(filename, encoding='utf-8') as f:
        self.assertEqual(actual, f.read())
    except (AssertionError, IOError):
      if SerializedCavernTest.update_resources:
        print(f'Updating {resource}')
        with open(filename, 'w', encoding='utf-8') as f:
          f.write(actual)
        self.assertTrue(True) # pylint: disable=redundant-unittest-assert
      else:
        raise


SerializedCavernTest.update_resources = False
