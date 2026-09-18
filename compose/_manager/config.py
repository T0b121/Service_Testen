"""Vorlagen sind Daten; weder Shellbefehle noch Variablenwerte werden ausgeführt."""
from dataclasses import dataclass
from pathlib import Path
import getpass
import re
import shlex
import yaml
from .model import ManagerError
from .state import private_write

NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
REF = re.compile(r'^(?:global\.|[a-z0-9-]+\.)?[A-Za-z_][A-Za-z0-9_]*$')


@dataclass
class Entry:
    stack: str
    variable: str
    key: str | None
    mode: str = ''
    default: str | None = None
    generate: str | None = None
    targets: tuple = ()
    literal: str | None = None


def unquote(value):
    value = value.strip()
    if value.startswith(('"', "'")):
        quote = value[0]
        escaped = False
        for i in range(1, len(value)):
            c = value[i]
            if c == quote and not escaped:
                tail = value[i + 1:].strip()
                if tail and not tail.startswith('#'):
                    raise ManagerError('Ungültiger Text nach zitiertem Wert.')
                inner = value[1:i]
                if quote == "'":
                    return inner.replace("\\'", "'")
                return re.sub(r'\\([nrt"\\])', lambda m: {'n':'\n','r':'\r','t':'\t'}.get(m[1], m[1]), inner)
            escaped = (c == '\\' and not escaped)
        raise ManagerError('Nicht geschlossenes Anführungszeichen.')
    return re.split(r'\s+#', value, maxsplit=1)[0].rstrip()


def lines(text):
    """Logische ENV-Zeilen, einschließlich zitierter mehrzeiliger Werte."""
    pending = ''
    for line in text.splitlines():
        pending = pending + '\n' + line if pending else line
        if not pending.strip() or pending.lstrip().startswith('#'):
            pending = ''
            continue
        if '=' not in pending:
            raise ManagerError('ENV-Zeile ohne Gleichheitszeichen.')
        name, value = pending.split('=', 1)
        if not NAME.fullmatch(name.strip()):
            raise ManagerError('Ungültiger ENV-Variablenname.')
        try:
            decoded = unquote(value)
        except ManagerError:
            if value.strip().startswith(('"', "'")):
                continue
            raise
        yield name.strip(), decoded
        pending = ''
    if pending:
        raise ManagerError('Unvollständiger ENV-Wert.')


def parse(stack, text):
    entries, variables = [], set()
    for variable, value in lines(text):
        if variable in variables:
            raise ManagerError(f'{stack}: doppelte Variable {variable}')
        variables.add(variable)
        m = re.fullmatch(r'([!-]?)<(.*)>', value, re.S)
        if not m:
            entries.append(Entry(stack, variable, None, literal=value))
            continue
        mode, expression = m.groups()
        lexer = shlex.shlex(expression, posix=True, punctuation_chars='|')
        lexer.whitespace = '|'
        lexer.whitespace_split = True
        lexer.commenters = ''
        pieces = [p.strip() for p in lexer if p.strip() and p != '|']
        head, *options = pieces
        key, sep, default = head.partition('=')
        key = key.strip()
        if not REF.fullmatch(key):
            raise ManagerError(f'{stack}: ungültige Referenz bei {variable}')
        if '.' not in key:
            key = f'{stack}.{key}'
        generate, targets = None, ()
        if sep and mode == '!':
            generate, default = default, None
        elif sep and mode == '-':
            targets, default = tuple(default.split(';')), None
        elif not sep:
            default = None
        seen = set()
        for option in options:
            name, eq, data = option.partition('=')
            name, data = name.strip(), data.strip()
            if not eq or name in seen or name not in ('generate', 'targets'):
                raise ManagerError(f'{stack}: ungültige Vorlagenoption bei {variable}')
            seen.add(name)
            if name == 'generate':
                generate = data
            else:
                targets = tuple(x.strip() for x in data.split(';') if x.strip())
        if mode == '-' and not targets:
            raise ManagerError(f'{stack}: Secret {variable} braucht targets=')
        if targets and mode != '-':
            raise ManagerError(f'{stack}: targets nur bei Datei-Secrets erlaubt')
        entries.append(Entry(stack, variable, key, mode, default, generate, targets))
    return entries


def read_env(path):
    return dict(lines(path.read_text())) if path.exists() else {}


def encode(value):
    # Compose: einfache Anführungszeichen verhindern $-Interpolation.
    return "'" + value.replace("'", "\\'") + "'"


def secret_path(stack, target):
    data = yaml.safe_load((stack.path / 'compose.yml').read_text())
    spec = data.get('secrets', {}).get(target, {})
    if not spec.get('file'):
        raise ManagerError(f'{stack.name}: unbekanntes Datei-Secret {target}')
    path = (stack.path / spec['file']).resolve()
    base = (stack.path / 'secrets').resolve()
    if not path.is_relative_to(base) or path == base:
        raise ManagerError(f'{stack.name}: Secret-Ziel muss im secrets-Verzeichnis liegen')
    return path


class Configuration:
    def __init__(self, stacks, selected):
        self.stacks = stacks
        self.entries = [e for n in selected for e in parse(n, (stacks[n].path / '.env.example').read_text())]
        self.values = {}
        self.grouped = {}
        for e in self.entries:
            if e.key:
                self.grouped.setdefault(e.key, []).append(e)
        for key, entries in self.grouped.items():
            for field in ('default', 'generate'):
                if len({getattr(e, field) for e in entries if getattr(e, field) is not None}) > 1:
                    raise ManagerError(f'Widersprüchliche {field}-Angaben für {key}')
            for e in entries:
                for target in e.targets:
                    secret_path(stacks[e.stack], target)
        self.load_existing()

    def load_existing(self):
        envs = {n: read_env(s.path / '.env') for n, s in self.stacks.items()}
        # Vorhandene Quellen auch bei ungewählten referenzierten Stacks beachten.
        source_entries = [e for n, s in self.stacks.items() for e in parse(n, (s.path / '.env.example').read_text())]
        for key in self.grouped:
            found = set()
            for e in source_entries:
                if e.key != key:
                    continue
                if e.mode != '-' and e.variable in envs[e.stack]:
                    found.add(envs[e.stack][e.variable])
                for target in e.targets:
                    path = secret_path(self.stacks[e.stack], target)
                    if path.exists():
                        found.add(path.read_text())
            if len(found) > 1:
                raise ManagerError(f'Vorhandene Werte für {key} widersprechen sich; Quellen abgleichen.')
            if found:
                self.values[key] = found.pop()

    def collect(self, ask=None):
        ask = ask or prompt_value
        for key, entries in self.grouped.items():
            if key in self.values:
                continue
            secret = any(e.mode in ('!', '-') for e in entries)
            default = next((e.default for e in entries if e.default is not None), None)
            hint = next((e.generate for e in entries if e.generate), None)
            value = ask(key, secret, default, hint)
            if not value:
                raise ManagerError(f'{key} darf nicht leer sein.')
            self.values[key] = value

    def write(self):
        missing = self.grouped.keys() - self.values.keys()
        if missing:
            raise ManagerError('Noch nicht erfasste Werte: ' + ', '.join(sorted(missing)))
        output = {}
        secrets = {}
        for e in self.entries:
            value = self.values[e.key] if e.key else e.literal
            if e.mode == '-':
                for target in e.targets:
                    path = secret_path(self.stacks[e.stack], target)
                    if path in secrets and secrets[path] != value:
                        raise ManagerError('Mehrere Werte für dasselbe Secret-Ziel.')
                    secrets[path] = value
            else:
                output.setdefault(e.stack, []).append(f'{e.variable}={encode(value)}')
        for path, value in secrets.items():
            private_write(path, value)
        for name, rows in output.items():
            private_write(self.stacks[name].path / '.env', '\n'.join(rows) + '\n')


def prompt_value(key, secret, default, hint):
    if hint:
        print(f'{key} – Erzeugungshinweis (selbst ausführen): {hint}')
    prompt = f'{key}' + (f' [{default}]' if default is not None and not secret else '') + ': '
    value = (getpass.getpass if secret else input)(prompt)
    if value.startswith('@file:'):
        return Path(value[6:]).expanduser().read_text()
    return value or default
