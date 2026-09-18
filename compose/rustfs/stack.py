AUTH_GROUPS = ['rustfs-admins', 'rustfs-users']

TITLE = 'rustfs'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['rustfs-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/rustfs.png',
  'routers': ['rustfs', 'rustfs-console'],
  'slug': 'rustfs',
  'title': 'rustfs'}]
SSO = {'type': 'oidc', 'slug': 'rustfs-console', 'client_id_env': 'RUSTFS_OIDC_CLIENT_ID', 'secret': 'rustfs_oidc_client_secret', 'callback': '/rustfs/admin/v3/oidc/callback/default', 'application': 'rustfs'}


def after_start(context):
    from _manager.docker import run
    stack = context.stacks['rustfs']
    command = '''set -eu
mc alias set local http://rustfs:9000 "$(cat /run/secrets/rustfs_root_access_key)" "$(cat /run/secrets/rustfs_root_secret_key)" >/dev/null
mc mb --ignore-existing local/langfuse >/dev/null
mc admin user add local "$(cat /run/secrets/langfuse_s3_access_key)" "$(cat /run/secrets/langfuse_s3_secret_key)" >/dev/null
mc admin policy create local stack-manager-langfuse /policy.json >/dev/null
mc admin policy attach local stack-manager-langfuse --user "$(cat /run/secrets/langfuse_s3_access_key)" >/dev/null
'''
    run(['docker', 'run', '--rm', '--network', 'rustfs_clients', '--entrypoint', '/bin/sh',
         '-v', str(stack.path / 'secrets') + ':/run/secrets:ro',
         '-v', str(stack.path / 'config/langfuse-policy.json') + ':/policy.json:ro',
         'minio/mc:RELEASE.2025-08-13T08-35-41Z', '-ec', command])
