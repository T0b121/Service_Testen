from .model import ManagerError


class Users:
    def __init__(self, auth, stacks, state, context):
        self.auth, self.stacks, self.state, self.context = auth, stacks, state, context

    def list(self):
        return [u for u in self.auth.items('core/users/') if u.get('type') == 'internal']

    def protect_admin(self, user):
        if user.get('is_superuser'):
            active = [u for u in self.list() if u.get('is_superuser') and u.get('is_active')]
            if len(active) <= 1 and user.get('is_active'):
                raise ManagerError('Der letzte aktive Administrator muss erhalten bleiben.')

    def create(self, username, name, email, password):
        user = self.auth.request('POST', 'core/users/', {
            'username': username, 'name': name, 'email': email, 'is_active': True,
            'type': 'internal', 'groups': []})
        try:
            self.auth.request('POST', f'core/users/{user["pk"]}/set_password/', {'password': password})
        except ManagerError:
            self.auth.request('PATCH', f'core/users/{user["pk"]}/', {'is_active': False})
            raise
        self.sync('create', user)
        return user

    def update(self, user, changes):
        if changes.get('is_active') is False:
            self.protect_admin(user)
        if set(changes) - {'name', 'email', 'is_active'}:
            raise ManagerError('Nur Name, E-Mail und Aktivierungsstatus werden zentral geändert; Login-ID bleibt stabil.')
        changed = self.auth.request('PATCH', f'core/users/{user["pk"]}/', changes)
        self.sync('update', changed)

    def permissions(self, user, wanted):
        # Nur aktiv verwaltete Dienstgruppen ersetzen, unabhängige Gruppen erhalten.
        managed_names = {g for n in self.state.data['selected'] for g in self.stacks[n].groups}
        groups = {g['name']: g['pk'] for g in self.auth.items('core/groups/')}
        if not set(wanted) <= managed_names or not set(wanted) <= groups.keys():
            raise ManagerError('Unbekannte Dienstgruppe ausgewählt.')
        managed_ids = {groups[g] for g in managed_names if g in groups}
        old = set(user.get('groups', []))
        new = (old - managed_ids) | {groups[g] for g in wanted}
        changed = self.auth.request('PATCH', f'core/users/{user["pk"]}/', {'groups': sorted(new)})
        self.sync('permissions', changed)

    def delete(self, user):
        self.protect_admin(user)
        # Zugriff zuerst sperren; lokale Konten vor Löschung aus Authentik behandeln.
        self.auth.request('PATCH', f'core/users/{user["pk"]}/', {'is_active': False})
        self.sync('delete', {**user, 'is_active': False})
        self.auth.request('DELETE', f'core/users/{user["pk"]}/')

    def sync(self, action, user):
        for name in self.state.data['selected']:
            stack = self.stacks[name]
            key = f'user:{user["pk"]}:{name}'
            entry = {'action': action, 'user': {k: user.get(k) for k in ('pk', 'username', 'name', 'email', 'is_active', 'groups')}}
            hook = getattr(stack.module, 'sync_user', None)
            if hook:
                try:
                    hook(self.context, action, entry['user'])
                    self.state.data['pending'].pop(key, None)
                except ManagerError:
                    entry['reason'] = 'Lokale Synchronisierung fehlgeschlagen; erneut versuchen.'
                    self.state.data['pending'][key] = entry
            elif getattr(stack.module, 'SSO', None):
                entry['reason'] = 'SSO überträgt unterstützte Angaben beim Login; lokale Konten/Sitzungen bei Bedarf in der Anwendung bearbeiten.'
                self.state.data['pending'][key] = entry
            else:
                entry['reason'] = 'Forward Auth aktualisiert den Zugang; lokale Anwendungskonten werden separat verwaltet.'
                self.state.data['pending'][key] = entry
            self.state.save()

    def retry(self):
        for key, entry in list(self.state.data['pending'].items()):
            if not key.startswith('user:') or not isinstance(entry, dict):
                continue
            name = key.rsplit(':', 1)[1]
            hook = getattr(self.stacks[name].module, 'sync_user', None)
            if hook:
                hook(self.context, entry['action'], entry['user'])
                del self.state.data['pending'][key]
                self.state.save()
