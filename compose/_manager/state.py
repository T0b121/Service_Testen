from contextlib import contextmanager
from pathlib import Path
import fcntl
import json
import os
import tempfile
from .model import ManagerError


def private_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ManagerError(f'Symbolischer Link als Konfigurationsziel nicht erlaubt: {path.name}')
    fd, name = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class State:
    def __init__(self, root):
        self.directory = Path(root) / '_state'
        self.path = self.directory / 'state.json'
        self.data = {'version': 1, 'selected': ['core'], 'completed': [], 'pending': {}, 'objects': {}, 'backups': []}
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text()))
            except (ValueError, OSError) as error:
                raise ManagerError('Verwaltungszustand kann nicht gelesen werden.') from error
            if self.data['version'] != 1:
                raise ManagerError('Unbekannte Version des Verwaltungszustands.')

    def save(self):
        private_write(self.path, json.dumps(self.data, indent=2, ensure_ascii=False) + '\n')

    @contextmanager
    def lock(self):
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        with (self.directory / 'manager.lock').open('a') as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ManagerError('Eine andere Verwaltung oder Sicherung läuft bereits.') from error
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
