"""Lokale Linux-Docker-Mounts sichern; Archive vor jeder Wiederherstellung prüfen."""
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import shutil
import stat
import tarfile
import tempfile
import uuid
from .docker import run
from .model import ManagerError


@dataclass
class Mount:
    source: str
    target: str
    kind: str
    name: str = ''
    eligible: bool = True
    reason: str = ''


def inventory(docker, stack, service):
    data = docker.config(stack)
    result = []
    for mount in data['services'][service].get('volumes', []):
        kind = mount['type']
        source, name = mount.get('source', ''), ''
        if kind == 'volume':
            if not source:
                result.append(Mount('', mount['target'], kind, eligible=False, reason='Anonymes Volume benötigt laufenden Container zur Zuordnung.'))
                continue
            name = data['volumes'][source]['name']
            source = json.loads(run(['docker', 'volume', 'inspect', name]))[0]['Mountpoint']
        path = Path(source)
        reason = ''
        if kind not in ('bind', 'volume'):
            reason = 'Kein persistenter Dateimount'
        elif not source or not path.exists():
            reason = 'Quelldaten fehlen oder Docker läuft nicht lokal'
        elif path.is_symlink():
            reason = 'Mount-Quelle ist ein symbolischer Link'
        elif not (path.is_dir() or path.is_file()):
            reason = 'Socket/Gerät ist nicht archivierbar'
        elif path.resolve() == Path('/') or '_backup' in path.parts:
            reason = 'Wurzelverzeichnis und Backup-Verzeichnis sind ausgeschlossen'
        result.append(Mount(source, mount['target'], kind, name, not reason, reason))
    # Secrets separat als Stack-Konfiguration sichern, keine Socket-/tmpfs-Einträge.
    return result


def overlapping(a, b):
    a, b = Path(a).resolve(), Path(b).resolve()
    return a == b or a.is_relative_to(b) or b.is_relative_to(a)


def users_of_mounts(mounts):
    ids = run(['docker', 'ps', '-q']).split()
    if not ids:
        return []
    containers = json.loads(run(['docker', 'inspect', *ids]))
    return [c['Id'] for c in containers if any(overlapping(m.source, x['Source'])
        for m in mounts for x in c.get('Mounts', []) if x.get('Source'))]


@contextmanager
def quiesce(mounts):
    running = users_of_mounts(mounts)
    try:
        if running:
            run(['docker', 'stop', '--time', '120', *running], timeout=300)
        yield
    finally:
        # Auch bei teilweise fehlgeschlagenem Stop die zuvor laufenden Dienste starten.
        if running:
            run(['docker', 'start', *running], timeout=300)


def inspect_archive(path):
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        names = set()
        for member in members:
            p = PurePosixPath(member.name)
            if p.is_absolute() or '..' in p.parts or member.name in names:
                raise ManagerError('Archiv enthält unsichere oder doppelte Pfade.')
            names.add(member.name)
            if not (member.isdir() or member.isfile() or member.issym() or member.islnk()):
                raise ManagerError('Archiv enthält Geräte, Sockets oder Sonderdateien.')
            if member.mode & 0o6000:
                raise ManagerError('Archiv enthält setuid/setgid-Dateien.')
        try:
            manifest_member = archive.getmember('manifest.json')
            if not manifest_member.isfile() or manifest_member.size > 1024 * 1024:
                raise ManagerError('Ungültiges Backup-Manifest.')
            manifest = json.load(archive.extractfile(manifest_member))
        except (KeyError, ValueError, TypeError) as error:
            raise ManagerError('Backup-Manifest fehlt oder ist ungültig.') from error
        if manifest.get('version') != 1 or not isinstance(manifest.get('mounts'), list):
            raise ManagerError('Nicht unterstütztes Archivformat.')
        if not 0 < len(manifest['mounts']) <= 1000:
            raise ManagerError('Ungültige Mount-Anzahl.')
        roots = {f'data/{i}' for i in range(len(manifest['mounts']))}
        for member in members:
            if member.name == 'manifest.json':
                continue
            root = '/'.join(PurePosixPath(member.name).parts[:2])
            if root not in roots:
                raise ManagerError('Archivpfad gehört zu keinem deklarierten Mount.')
            parents = PurePosixPath(member.name).parents
            for parent in parents:
                if str(parent) in names:
                    entry = archive.getmember(str(parent))
                    if entry.issym() or entry.islnk():
                        raise ManagerError('Archiv enthält Dateien unter einem Link.')
            if member.issym() or member.islnk():
                target = PurePosixPath(member.linkname)
                if target.is_absolute():
                    raise ManagerError('Absolute Archivlinks sind nicht erlaubt.')
                # Normalisieren, ohne auf dem Host Links aufzulösen.
                parts = list(PurePosixPath(member.name).parent.parts) if member.issym() else []
                for part in target.parts:
                    if part == '..':
                        if not parts:
                            raise ManagerError('Archivlink verlässt das Ziel.')
                        parts.pop()
                    elif part != '.':
                        parts.append(part)
                if '/'.join(parts[:2]) != root:
                    raise ManagerError('Archivlink verlässt seinen Mount.')
                if member.islnk() and '/'.join(parts) not in names:
                    raise ManagerError('Hardlink-Ziel fehlt.')
        for root in roots:
            if root not in names or not (archive.getmember(root).isfile() or archive.getmember(root).isdir()):
                raise ManagerError('Mount-Wurzel fehlt oder ist kein regulärer Datenbestand.')
        return manifest


def export_archive(output, stack, service, mounts, *, stop=True, config=None, recipient=None):
    output = Path(output)
    if not mounts or any(not m.eligible for m in mounts):
        raise ManagerError('Keine gültigen Mounts gewählt.')
    mounts = list(mounts)
    if config:
        if not recipient:
            raise ManagerError('Stack-Konfiguration mit Secrets benötigt einen age-Empfänger.')
        for name in ('.env', 'secrets'):
            path = Path(config) / name
            if path.exists():
                mounts.append(Mount(str(path), name, 'configuration'))
    for i, mount in enumerate(mounts):
        if Path(mount.source).is_dir() and output.resolve().is_relative_to(Path(mount.source).resolve()):
            raise ManagerError('Backup-Ziel liegt innerhalb der gesicherten Daten.')
        if any(overlapping(mount.source, other.source) for other in mounts[:i]):
            raise ManagerError('Überlappende Mounts nur einmal auswählen.')
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if output.exists():
        raise ManagerError('Backup-Zieldatei existiert bereits.')
    with tempfile.TemporaryDirectory(prefix='.backup-', dir=output.parent) as temp:
        tarpath = Path(temp) / 'archive.tar.gz'
        manifest = {'version': 1, 'stack': stack, 'service': service,
                    'created': datetime.now(timezone.utc).isoformat(), 'method': 'stopped',
                    'mounts': [asdict(m) for m in mounts]}
        from io import BytesIO
        with quiesce(mounts):
            with tarfile.open(tarpath, 'w:gz', format=tarfile.PAX_FORMAT, dereference=False) as archive:
                raw = json.dumps(manifest).encode()
                info = tarfile.TarInfo('manifest.json'); info.size = len(raw); info.mode = 0o600
                archive.addfile(info, BytesIO(raw))
                for i, mount in enumerate(mounts):
                    archive.add(mount.source, arcname=f'data/{i}', recursive=True)
        os.chmod(tarpath, 0o600)
        inspect_archive(tarpath)
        if recipient:
            encrypted = Path(temp) / 'archive.age'
            run(['age', '-r', recipient, '-o', str(encrypted), str(tarpath)])
            os.chmod(encrypted, 0o600)
            os.replace(encrypted, output)
        else:
            os.replace(tarpath, output)
    return output


def import_archive(archive_path, targets, *, identity=None, replace=False):
    if not replace:
        raise ManagerError('Import benötigt die ausdrückliche Auswahl „Zieldaten ersetzen“.')
    with tempfile.TemporaryDirectory(prefix='stack-import-') as temp:
        path = Path(archive_path)
        if path.name.endswith('.age'):
            if not identity:
                raise ManagerError('Verschlüsseltes Archiv benötigt eine age-Identitätsdatei.')
            plain = Path(temp) / 'archive.tar.gz'
            run(['age', '-d', '-i', str(identity), '-o', str(plain), str(path)])
            path = plain
        manifest = inspect_archive(path)
        if any(not isinstance(i, int) or i < 0 or i >= len(manifest['mounts']) for i in targets):
            raise ManagerError('Ungültige Archiv-Mount-Auswahl.')
        if not targets:
            raise ManagerError('Keine Importziele ausgewählt.')
        destinations = [Path(p).resolve() for p in targets.values()]
        for i, dst in enumerate(destinations):
            if dst == Path('/') or any(overlapping(dst, p) for p in destinations[:i]):
                raise ManagerError('Überlappende oder ungültige Importziele.')
            if dst.is_dir() and path.resolve().is_relative_to(dst):
                raise ManagerError('Archiv darf nicht innerhalb des Importziels liegen.')
        mounts = [Mount(str(p), '', 'bind') for p in destinations]
        # Extraktion in frische temporäre Verzeichnisse, nie direkt in vorhandene Links.
        stages, completed = [], []
        try:
            with quiesce(mounts), tarfile.open(path, 'r:gz') as archive:
                for index, target in targets.items():
                    target = Path(target)
                    if target.is_symlink():
                        raise ManagerError('Importziel darf kein symbolischer Link sein.')
                    target = target.resolve()
                    target.parent.mkdir(parents=True, exist_ok=True)
                    stage = Path(tempfile.mkdtemp(prefix='.restore-', dir=target.parent))
                    stages.append(stage)
                    prefix = f'data/{index}'
                    members = [m for m in archive.getmembers() if m.name == prefix or m.name.startswith(prefix + '/')]
                    archive.extractall(stage, members=members, filter='fully_trusted')  # Vollständige eigene Prüfung oben.
                    staged = stage / prefix
                    # Docker-Volumes: Verzeichnis selbst bleibt bestehen; Inhalt atomar je Eintrag tauschen.
                    old = stage / 'previous'; old.mkdir()
                    if target.exists() and target.is_dir() != staged.is_dir():
                        raise ManagerError('Datei/Verzeichnis-Typ passt nicht zum Importziel.')
                    if staged.is_dir():
                        target.mkdir(exist_ok=True)
                        previous = list(target.iterdir())
                        for child in previous:
                            os.replace(child, old / child.name)
                        installed = []
                        try:
                            for child in staged.iterdir():
                                os.replace(child, target / child.name); installed.append(target / child.name)
                            shutil.copystat(staged, target)
                            if os.geteuid() == 0:
                                os.chown(target, staged.stat().st_uid, staged.stat().st_gid)
                        except BaseException:
                            for child in installed:
                                if child.is_dir() and not child.is_symlink(): shutil.rmtree(child)
                                else: child.unlink()
                            for child in old.iterdir(): os.replace(child, target / child.name)
                            raise
                    else:
                        if target.exists(): shutil.copy2(target, old / 'file')
                        os.replace(staged, target)
                    completed.append(str(target))
        except BaseException as error:
            if completed:
                raise ManagerError('Import nach Teilwiederherstellung abgebrochen. Bereits ersetzt: ' + ', '.join(completed)) from error
            raise
        finally:
            for stage in stages:
                shutil.rmtree(stage, ignore_errors=True)
        return manifest
