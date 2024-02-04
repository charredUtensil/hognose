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
  
  def assertDioramaMatches(self, diorama: Diorama, resource: str):
    filename = os.path.join(RESOURCE_DIR, f'{resource}.dat')
    actual = sanitize(diorama.serialize())
    try:
      with open(filename) as f:
        self.assertEqual(actual, f.read())
    except (AssertionError, IOError):
      if SerializedCavernTest.update_resources:
        print(f'Updating {resource}')
        with open(filename, 'w') as f:
          f.write(actual)
        self.assertTrue(True)
      else:
        raise

SerializedCavernTest.update_resources = False