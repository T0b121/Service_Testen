from pathlib import Path
import getpass
import json
import os
from prompt_toolkit.shortcuts import checkboxlist_dialog, radiolist_dialog, yes_no_dialog
from .config import read_env, parse, lines
from .model import ManagerError, order
from .state import private_write
from .users import Users
from .backup import inventory, export_archive, inspect_archive, import_archive, users_of_mounts
from .scheduler import add_job, describe, install_timer


def choose(title, values, default=None):
    return radiolist_dialog(title=title, text='Auswählen und bestätigen', values=values,
                            default=default).run()


def checks(title, values, defaults=()):
    return checkboxlist_dialog(title=title, text='Leertaste: auswählen · Tab: zu OK/Abbrechen',
                               values=values, default_values=list(defaults)).run()


def select_stacks(context):
    selected = checks('Stacks auswählen – core ist immer aktiv',
        [(n, s.title) for n, s in context.stacks.items() if n != 'core'],
        [n for n in context.state.data.get('desired', context.state.data['selected']) if n != 'core'])
    if selected is None:
        return
    resolved = order(context.stacks, selected)
    print('Auswahl einschließlich Abhängigkeiten: ' + ', '.join(resolved))
    if yes_no_dialog(title='Einrichtung', text='Diese Stacks konfigurieren und starten?\n' + ', '.join(resolved)).run():
        context.initialize(resolved)


def edit_text(title, text):
    from prompt_toolkit import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.widgets import TextArea, Frame
    field = TextArea(text=text, multiline=True, scrollbar=True, line_numbers=True)
    keys = KeyBindings()
    @keys.add('c-s')
    def save(event): event.app.exit(result=field.text)
    @keys.add('c-q')
    def cancel(event): event.app.exit(result=None)
    return Application(layout=Layout(Frame(field, title=title + ' | Ctrl-S Speichern · Ctrl-Q Abbrechen')),
                       key_bindings=keys, full_screen=True).run()


def edit_config(context):
    name = choose('Konfiguration bearbeiten', [(n, s.title) for n, s in context.stacks.items() if (s.path / '.env').exists()])
    if not name:
        return
    stack = context.stacks[name]; path = stack.path / '.env'; old = path.read_text()
    result = edit_text(name + '/.env (enthält ggf. Geheimnisse)', old)
    if result is None or result == old:
        return
    previous, changed = dict(lines(old)), dict(lines(result))
    entries = parse(name, (stack.path / '.env.example').read_text())
    for entry in entries:
        if entry.mode == '!' and changed.get(entry.variable) != previous.get(entry.variable):
            raise ManagerError('Passwortänderung benötigt die passende Änderung im laufenden Dienst; nicht nur die ENV-Datei ändern.')
    originals = {path: old}
    updates = {path: result}
    shared = {e.key: changed[e.variable] for e in entries if e.key and e.mode != '-'
              and e.variable in changed and changed[e.variable] != previous.get(e.variable)}
    from .config import encode
    for other in context.stacks.values():
        other_path = other.path / '.env'
        if other_path == path or not other_path.exists():
            continue
        values = read_env(other_path)
        dirty = False
        for entry in parse(other.name, (other.path / '.env.example').read_text()):
            if entry.key in shared and entry.mode != '-':
                if entry.mode == '!':
                    raise ManagerError('Ein gemeinsam verwendetes Geheimnis darf nicht als normale ENV-Änderung rotiert werden.')
                values[entry.variable] = shared[entry.key]; dirty = True
        if dirty:
            originals[other_path] = other_path.read_text()
            updates[other_path] = '\n'.join(k + '=' + encode(v) for k,v in values.items()) + '\n'
    try:
        for dest, content in updates.items(): private_write(dest, content)
        context.check_templates()
        for dest in updates: context.docker.compose(dest.parent.name, 'config', '--quiet')
    except Exception:
        for dest, content in originals.items(): private_write(dest, content)
        raise
    print(f'{name}: Konfiguration gespeichert; Container werden neu erstellt.')
    context.initialize(context.state.data['selected'])


def user_menu(context):
    users = Users(context.auth, context.stacks, context.state, context)
    action = choose('Nutzerverwaltung', [(x,x) for x in ['Erstellen','Bearbeiten','Berechtigungen','Löschen','Synchronisierung erneut versuchen']])
    if not action: return
    if action == 'Synchronisierung erneut versuchen': users.retry(); return
    if action == 'Erstellen':
        users.create(input('Benutzername: '), input('Name: '), input('E-Mail: '), getpass.getpass('Passwort: ')); return
    entries = users.list()
    pk = choose('Nutzer auswählen', [(u['pk'], f'{u["username"]} – {u["name"]}') for u in entries])
    if pk is None: return
    user = next(u for u in entries if u['pk'] == pk)
    if action == 'Bearbeiten':
        users.update(user, {'name': input(f'Name [{user["name"]}]: ') or user['name'],
                            'email': input(f'E-Mail [{user["email"]}]: ') or user['email'],
                            'is_active': yes_no_dialog(title='Nutzerstatus', text='Nutzer aktivieren?').run()})
    elif action == 'Löschen':
        if yes_no_dialog(title='Nutzer löschen', text=f'{user["username"]} wirklich aus Authentik löschen?').run(): users.delete(user)
    else:
        groups = {g['pk']: g['name'] for g in context.auth.items('core/groups/')}
        wanted = checks('Dienstberechtigungen', [(g, f'{n} → {g}') for n in context.state.data['selected'] for g in context.stacks[n].groups],
                        [groups[g] for g in user.get('groups', []) if g in groups])
        if wanted is not None: users.permissions(user, wanted)


def select_mounts(context):
    name = choose('Stack auswählen', [(n,n) for n in context.state.data['selected']])
    if not name: return None
    data = context.docker.config(name)
    service = choose('Service auswählen', [(s,s) for s in data['services']])
    if not service: return None
    mounts = inventory(context.docker, name, service)
    for mount in mounts:
        if not mount.eligible: print(f'{mount.target}: nicht sicherbar – {mount.reason}')
    ids = checks('Mounts auswählen', [(i, f'{m.kind}: {m.source} → {m.target}') for i,m in enumerate(mounts) if m.eligible])
    if not ids: return None
    selected = [mounts[i] for i in ids]
    containers = users_of_mounts(selected)
    print(f'{len(containers)} laufende Container verwenden diese Daten und werden vorübergehend gestoppt.')
    return name, service, selected


def backup_menu(context):
    action = choose('Backups / Import / Export', [(x,x) for x in ['Export','Import','Zeitplan erstellen','Zeitpläne anzeigen','Zeitplan löschen','Automatische Ausführung installieren']])
    if not action: return
    if action == 'Automatische Ausführung installieren': install_timer(context.root); return
    if action == 'Zeitpläne anzeigen':
        for job in context.state.data['backups']: print(json.dumps(job, indent=2, ensure_ascii=False))
        return
    if action == 'Zeitplan löschen':
        jobs = context.state.data['backups']
        key = choose('Zeitplan löschen (Archive bleiben erhalten)', [(j['id'], j['stack']+'/'+j['service']+' '+j['cron']) for j in jobs])
        if key: context.state.data['backups'] = [j for j in jobs if j['id'] != key]; context.state.save()
        return
    selected = select_mounts(context)
    if not selected: return
    name, service, mounts = selected
    if action == 'Import':
        path = Path(input('Archivpfad: ')).expanduser()
        if path.name.endswith('.age'):
            identity = Path(input('age-Identitätsdatei: ')).expanduser()
            from tempfile import TemporaryDirectory
            from .docker import run
            with TemporaryDirectory() as folder:
                plain = Path(folder) / 'import.tar.gz'
                run(['age', '-d', '-i', str(identity), '-o', str(plain), str(path)])
                _import(plain, mounts, context.stacks[name].path)
        else: _import(path, mounts, context.stacks[name].path)
        return
    config = yes_no_dialog(title='Konfiguration', text='ENV und Secrets zusätzlich verschlüsselt mitsichern?').run()
    recipient = input('age-Empfänger (age1…): ').strip() if config else None
    if action == 'Export':
        from datetime import datetime, timezone
        default = context.root / '_backup' / name / service / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.tar.gz' + ('.age' if recipient else ''))
        output = Path(input(f'Zieldatei [{default}]: ') or default)
        print(export_archive(output, name, service, mounts, config=context.stacks[name].path if config else None, recipient=recipient))
    else:
        expression = input('Cron [0 3 * * *]: ') or '0 3 * * *'
        zone = input('Zeitzone [Europe/Berlin]: ') or 'Europe/Berlin'
        print(describe(expression, zone))
        keep = int(input('Anzahl erfolgreicher Backups [7]: ') or 7)
        add_job(context.state, name, service, [m.target for m in mounts], expression, zone, keep, config, recipient)
        print('Zeitplan gespeichert. Für unbeaufsichtigte Ausführung den Timer über das Backup-Menü installieren.')


def _import(path, mounts, stack_path):
    manifest = inspect_archive(path)
    targets = {}
    for i, item in enumerate(manifest['mounts']):
        options = [(m.source, m.target) for m in mounts]
        if item.get('kind') == 'configuration' and item.get('target') in ('.env', 'secrets'):
            options = [(str(stack_path / item['target']), 'Stack-Konfiguration: ' + item['target'])]
        dest = choose(f'Archiv-Mount {item["target"]}: Ziel wählen', [('', 'Überspringen'), *options])
        if dest: targets[i] = dest
    if targets and yes_no_dialog(title='Zieldaten ersetzen', text='Alle vorhandenen Daten in den gewählten Mounts ersetzen?\n' + '\n'.join(targets.values())).run():
        import_archive(path, targets, replace=True)


def menu(context):
    while True:
        action = choose('Compose Stack Manager', [(x,x) for x in ['Ersteinrichtung','Start','Konfiguration bearbeiten','Stop','Neustart','Stack-Auswahl ändern','Nutzerverwaltung','Backups / Import / Export','Status','Beenden']])
        if not action or action == 'Beenden': return
        try:
            with context.state.lock():
                if action in ('Ersteinrichtung','Stack-Auswahl ändern'): select_stacks(context)
                elif action == 'Start': context.start()
                elif action == 'Stop': context.docker.stop(context.state.data['selected'])
                elif action == 'Neustart':
                    context.docker.stop(context.state.data['selected']); context.start()
                elif action == 'Konfiguration bearbeiten': edit_config(context)
                elif action == 'Nutzerverwaltung': user_menu(context)
                elif action == 'Backups / Import / Export': backup_menu(context)
                elif action == 'Status': print(json.dumps(context.state.data, ensure_ascii=False, indent=2))
        except (ManagerError, OSError, ValueError) as error:
            print('Fehler: ' + str(error))
        input('Enter zum Menü …')
