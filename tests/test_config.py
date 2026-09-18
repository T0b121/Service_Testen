import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'compose'))
from _manager.config import parse, lines, encode
from _manager.model import ManagerError

class Templates(unittest.TestCase):
    def test_shared_secret_and_generation(self):
        entries = parse('db', '''PW=!<DB_PW | generate="openssl rand -hex 32">
FILE=-<DB_PW | targets=db_password;other>
DOMAIN=<global.DOMAIN>
NAME=<NAME=Mein Server> # Kommentar
''')
        self.assertEqual(entries[0].key, entries[1].key)
        self.assertEqual(entries[0].generate, 'openssl rand -hex 32')
        self.assertEqual(entries[1].targets, ('db_password', 'other'))
        self.assertEqual(entries[3].default, 'Mein Server')

    def test_literal_roundtrip(self):
        for value in ['a$B#c=d', "it's secret", 'line1\nline2', r'a\b', '#hash', '']:
            self.assertEqual(dict(lines('X=' + encode(value)))['X'], value)

    def test_duplicate_rejected(self):
        with self.assertRaises(ManagerError):
            parse('x', 'A=1\nA=2')

    def test_json_default_keeps_quotes(self):
        self.assertEqual(parse('x', 'M=<M={"*":-1}>')[0].default, '{"*":-1}')
