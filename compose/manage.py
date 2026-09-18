#!/usr/bin/env python3
"""Aufruf ohne Argumente startet das Terminalmenü."""
import argparse
from pathlib import Path
import sys
from _manager.lifecycle import Context
from _manager.model import ManagerError


def main():
    parser = argparse.ArgumentParser(description='Compose Stack Manager')
    parser.add_argument('command', nargs='?', default='menu', choices=['menu','check','list','start','stop','restart','setup','backup-tick','install-timer'])
    parser.add_argument('--stacks', nargs='+', help='Bei setup gewünschte Stack-Namen; core wird ergänzt')
    args = parser.parse_args()
    context = Context(Path(__file__).resolve().parent)
    if args.command == 'menu':
        from _manager.ui import menu
        menu(context); return
    with context.state.lock():
        if args.command == 'check': context.check_templates(); print('Alle Stack-Vorlagen erfolgreich geprüft.')
        elif args.command == 'list':
            for name, stack in context.stacks.items(): print(f'{name}: benötigt {", ".join(stack.requires) or "–"}')
        elif args.command == 'setup': context.initialize(args.stacks or context.state.data['selected'])
        elif args.command == 'start': context.start()
        elif args.command == 'stop': context.docker.stop(context.state.data['selected'])
        elif args.command == 'restart': context.docker.stop(context.state.data['selected']); context.start()
        elif args.command == 'backup-tick':
            from _manager.scheduler import tick
            tick(context)
        elif args.command == 'install-timer':
            from _manager.scheduler import install_timer
            install_timer(context.root)


if __name__ == '__main__':
    try:
        main()
    except (ManagerError, OSError, ValueError) as error:
        print('Fehler: ' + str(error), file=sys.stderr); sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print('\nAbgebrochen.', file=sys.stderr); sys.exit(130)
