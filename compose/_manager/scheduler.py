from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import os
import re
import sys
from .backup import inventory, export_archive
from .docker import run
from .model import ManagerError
from .state import private_write


def next_run(expression, zone, after=None):
    from croniter import croniter
    if len(expression.split()) != 5 or not croniter.is_valid(expression):
        raise ManagerError('Cron-Ausdruck benötigt fünf gültige Felder (Minute Stunde Tag Monat Wochentag).')
    try:
        tz = ZoneInfo(zone)
    except (KeyError, ValueError) as error:
        raise ManagerError('Unbekannte Zeitzone.') from error
    base = (after or datetime.now(timezone.utc)).astimezone(tz)
    return croniter(expression, base).get_next(datetime).astimezone(timezone.utc)


def describe(expression, zone):
    values = expression.split()
    if len(values) == 5 and values[0].isdigit() and values[1].isdigit() and values[2:] == ['*', '*', '*']:
        return f'Täglich um {int(values[1]):02d}:{int(values[0]):02d} ({zone})'
    return f'Cron {expression} ({zone}), nächster Lauf: {next_run(expression, zone).isoformat()}'


def add_job(state, stack, service, targets, expression, zone, keep, config=False, recipient=None):
    if not isinstance(keep, int) or keep < 1:
        raise ManagerError('Mindestens ein erfolgreiches Backup behalten.')
    if not targets:
        raise ManagerError('Mindestens einen Mount auswählen.')
    if config and not recipient:
        raise ManagerError('Konfigurationsbackup benötigt age-Verschlüsselung.')
    import uuid
    job = {'id': uuid.uuid4().hex, 'stack': stack, 'service': service, 'targets': targets,
           'cron': expression, 'timezone': zone, 'keep': keep, 'configuration': config,
           'recipient': recipient, 'next': next_run(expression, zone).isoformat(), 'archives': []}
    state.data['backups'].append(job); state.save()
    return job


def tick(context):
    now = datetime.now(timezone.utc)
    for job in context.state.data['backups']:
        if datetime.fromisoformat(job['next']) > now:
            continue
        try:
            mounts = inventory(context.docker, job['stack'], job['service'])
            selected = [m for m in mounts if m.target in job['targets']]
            if len(selected) != len(job['targets']):
                raise ManagerError('Mount-Auswahl hat sich geändert; Backupauftrag prüfen.')
            folder = context.root / '_backup' / job['stack'] / job['service']
            suffix = '.tar.gz.age' if job.get('recipient') else '.tar.gz'
            filename = now.strftime('%Y%m%dT%H%M%SZ') + '-' + job['id'] + suffix
            path = export_archive(folder / filename, job['stack'], job['service'], selected,
                config=context.stacks[job['stack']].path if job.get('configuration') else None,
                recipient=job.get('recipient'))
            job['archives'].append(path.name)
            # Nur diesem Auftrag zugeordnete Archive nach erfolgreicher Sicherung entfernen.
            while len(job['archives']) > job['keep']:
                old = job['archives'][0]
                if Path(old).name != old:
                    raise ManagerError('Ungültiger Archivname im Verwaltungszustand.')
                (folder / old).unlink(missing_ok=True)
                job['archives'].pop(0)
            job['last_success'] = now.isoformat(); job.pop('error', None)
        except (ManagerError, OSError) as error:
            job['error'] = str(error)
        finally:
            # Keine endlosen Wiederholungen desselben fehlgeschlagenen Termins.
            job['next'] = next_run(job['cron'], job['timezone'], now).isoformat()
            context.state.save()


def install_timer(root):
    if os.geteuid() != 0:
        raise ManagerError('Der systemd-Timer muss als root installiert werden.')
    script = Path(root) / 'manage.py'
    def quote(value):
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%') + '"'
    unit = ('[Unit]\nDescription=Compose Stack Manager Backups\nAfter=docker.service\nRequires=docker.service\n'
            '[Service]\nType=oneshot\nUMask=0077\n'
            f'ExecStart={quote(sys.executable)} {quote(script)} backup-tick\n')
    timer = ('[Unit]\nDescription=Check stack backup schedules every minute\n[Timer]\n'
             'OnCalendar=*-*-* *:*:00\nPersistent=true\n[Install]\nWantedBy=timers.target\n')
    private_write(Path('/etc/systemd/system/stack-manager-backup.service'), unit)
    private_write(Path('/etc/systemd/system/stack-manager-backup.timer'), timer)
    run(['systemctl', 'daemon-reload'])
    run(['systemctl', 'enable', '--now', 'stack-manager-backup.timer'])
