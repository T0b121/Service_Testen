"""Compose-Dateisecrets benötigen lesbare Bind-Mount-Rechte auch für Non-root-Images."""
from pathlib import Path
import grp
import os
from .docker import run
from .model import ManagerError

SECRETS_GID = 60001


def ensure_secret_group():
    if os.geteuid() != 0:
        raise ManagerError('Einrichtung als root ausführen: sudo .venv/bin/python compose/manage.py. Dateisecrets und Mount-Backups benötigen lokale Dateirechte.')
    try:
        group = grp.getgrgid(SECRETS_GID)
    except KeyError:
        run(['groupadd', '--system', '--gid', str(SECRETS_GID), 'stack-manager-secrets'])
    else:
        if group.gr_name != 'stack-manager-secrets':
            raise ManagerError(f'GID {SECRETS_GID} ist bereits vergeben; Secret-GID vor Installation im Manager und Compose-Dateien anpassen.')


def prepare_secrets(stack):
    directory = stack.path / 'secrets'
    if not directory.exists():
        return
    os.chown(directory, -1, SECRETS_GID)
    os.chmod(directory, 0o750)
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ManagerError(f'{stack.name}: nur reguläre Secret-Dateien zulässig.')
        os.chown(path, -1, SECRETS_GID)
        os.chmod(path, 0o640)
