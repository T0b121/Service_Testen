import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'compose'))
from _manager.model import Stack, order, ManagerError

class Dependencies(unittest.TestCase):
    def test_dependency_closure_and_cycle(self):
        stacks = {n: Stack(n, Path(n), n, deps) for n, deps in [('core', []), ('db', ['core']), ('app', ['db'])]}
        self.assertEqual(order(stacks, ['app']), ['core', 'db', 'app'])
        stacks['db'].requires.append('app')
        with self.assertRaises(ManagerError):
            order(stacks, ['app'])

    def test_missing(self):
        with self.assertRaises(ManagerError):
            order({'core': Stack('core', Path('.'), 'core')}, ['missing'])
