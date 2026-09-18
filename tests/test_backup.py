import io, json, pathlib, sys, tarfile, tempfile, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'compose'))
from _manager.backup import inspect_archive
from _manager.model import ManagerError

class Archives(unittest.TestCase):
    def make(self, name, link=None):
        temp = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False); temp.close()
        self.addCleanup(pathlib.Path(temp.name).unlink)
        with tarfile.open(temp.name, 'w:gz') as a:
            m=json.dumps({'version':1,'mounts':[{}]}).encode(); t=tarfile.TarInfo('manifest.json');t.size=len(m);a.addfile(t,io.BytesIO(m))
            t=tarfile.TarInfo('data/0');t.type=tarfile.DIRTYPE;a.addfile(t)
            t=tarfile.TarInfo(name)
            if link: t.type=tarfile.SYMTYPE;t.linkname=link
            a.addfile(t)
        return temp.name
    def test_traversal_rejected(self):
        for name,link in [('../escape',None),('/absolute',None),('data/0/link','../../outside'),('data/0/link','/etc/passwd')]:
            with self.assertRaises(ManagerError):inspect_archive(self.make(name,link))
    def test_regular_archive(self):
        self.assertEqual(inspect_archive(self.make('data/0/test'))['version'],1)

class Schedules(unittest.TestCase):
    def test_timezone_and_retention_config(self):
        try:
            import croniter
        except ImportError:
            self.skipTest('croniter nicht installiert')
        from datetime import datetime, timezone
        from _manager.scheduler import next_run
        result=next_run('0 3 * * *', 'Europe/Berlin', datetime(2026,1,1,tzinfo=timezone.utc))
        self.assertEqual(result.hour, 2)
        with self.assertRaises(ManagerError):next_run('* * * * * *','UTC')
