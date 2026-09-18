AUTH_GROUPS = ['partdb-admin', 'partdb-editor', 'partdb-readonly']

TITLE = 'partdb'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['partdb-admin', 'partdb-editor', 'partdb-readonly'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/part-db.png',
  'routers': ['partdb'],
  'slug': 'partdb',
  'title': 'partdb'}]
SSO = {'type': 'saml', 'slug': 'partdb-sso', 'application': 'partdb', 'acs': '/saml/acs', 'audience': '/sp'}


def after_start(context):
    import json
    from _manager.config import read_env, encode
    from _manager.state import private_write
    from _manager.model import ManagerError
    # DB_AUTOMIGRATE bleibt allein für Migrationen zuständig.
    raw = context.docker.exec('partdb', 'partdb', '/manager-entrypoint.sh', 'manager-groups')
    groups = json.loads(raw)
    required = {'partdb-admin': 'admins', 'partdb-editor': 'users', 'partdb-readonly': 'readonly'}
    if not set(required.values()) <= groups.keys():
        raise ManagerError('Part-DB-Standardgruppen fehlen; keine numerischen Gruppen-IDs erraten.')
    mapping = {role: groups[name] for role, name in required.items()}
    mapping['*'] = -1
    path = context.stacks['partdb'].path / '.env'
    values = read_env(path)
    values['PARTDB_SAML_ROLE_MAPPING'] = json.dumps(mapping, separators=(',', ':'))
    private_write(path, '\n'.join(k + '=' + encode(v) for k,v in values.items()) + '\n')
    context.docker.exec('partdb', 'partdb', '/manager-entrypoint.sh', 'console',
                        'partdb:users:permissions', 'anonymous', '--edit', input='*\nD\n')
    context.docker.compose('partdb', 'up', '-d', '--no-deps', '--force-recreate', '--wait', 'partdb')


def before_start(context):
    from _manager.docker import run
    from _manager.model import ManagerError
    path = context.stacks['partdb'].path / 'secrets'
    public_certificate = run(['openssl', 'x509', '-in', str(path / 'partdb_saml_sp_certificate'), '-pubkey', '-noout'])
    public_key = run(['openssl', 'pkey', '-in', str(path / 'partdb_saml_sp_private_key'), '-pubout'])
    if public_certificate.strip() != public_key.strip():
        raise ManagerError('Part-DB: SAML-Zertifikat und privater Schlüssel gehören nicht zusammen.')
