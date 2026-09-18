import json
import re
from .config import read_env
from .docker import routes
from .model import ManagerError
from .state import private_write


def provision(auth, stack):
    spec = getattr(stack.module, 'SSO', None)
    if not spec:
        return
    env = read_env(stack.path / '.env')
    app = next(a for a in stack.applications if a['slug'] == spec['application'])
    route = routes(auth.docker.config(stack.name))[app['routers'][0]]
    host = re.search(r'Host\(`([^`]+)`\)', route['rule'])[1]
    url = 'https://' + host
    groups = auth.groups(stack)
    common = {'authorization_flow': auth.flow('default-provider-authorization-implicit-consent'),
              'invalidation_flow': auth.flow('default-provider-invalidation-flow'),
              'authentication_flow': auth.flow('default-authentication-flow')}
    keys = auth.items('crypto/certificatekeypairs/')
    key = next((k for k in keys if k.get('name') == 'authentik Self-signed Certificate'), None)
    if key is None:
        raise ManagerError('Authentik-Signaturzertifikat fehlt.')
    if spec['type'] == 'oidc':
        path = stack.path / 'secrets' / spec['secret']
        secret = path.read_text() if path.exists() else env[spec['secret']]
        client = env[spec['client_id_env']] if spec.get('client_id_env') else spec['slug']
        mapping = auth.ensure('propertymappings/provider/scope/', {'name': 'stack-manager:groups'}, {
            'scope_name': 'groups', 'expression': 'return {"groups": list(request.user.groups.values_list("name", flat=True))}'})
        mappings = [m['pk'] for m in auth.items('propertymappings/provider/scope/')
                    if m.get('managed') in ('goauthentik.io/providers/oauth2/scope-openid',
                        'goauthentik.io/providers/oauth2/scope-profile', 'goauthentik.io/providers/oauth2/scope-email')]
        if len(mappings) != 3:
            raise ManagerError('OIDC-Standard-Mappings fehlen.')
        if stack.name == 'open-webui':
            role = auth.ensure('propertymappings/provider/scope/', {'name': 'stack-manager:open-webui-roles'}, {
                'scope_name': 'roles', 'expression': 'return {"roles": ["admin"] if ak_is_group_member(request.user, "open-webui-admins") else ["user"]}'})
            mappings.append(role['pk'])
        if stack.name == 'nextcloud':
            mapping = auth.ensure('propertymappings/provider/scope/', {'name': 'stack-manager:nextcloud-groups'}, {
                'scope_name': 'groups', 'expression': 'return {"groups": list(request.user.groups.values_list("name", flat=True)) + (["admin"] if ak_is_group_member(request.user, "nextcloud-admins") else [])}'})
        provider = auth.ensure('providers/oauth2/', {'name': 'stack-manager:' + spec['slug']}, {
            **common, 'client_id': client, 'client_secret': secret, 'client_type': 'confidential',
            'signing_key': key['pk'], 'property_mappings': [*mappings, mapping['pk']],
            'include_claims_in_id_token': True, 'sub_mode': 'user_id',
            'redirect_uris': [{'matching_mode': 'strict', 'url': url + spec['callback']}]})
        if stack.name == 'paperless':
            config = {'openid_connect': {'APPS': [{'provider_id': 'authentik', 'name': 'Authentik',
                'client_id': client, 'secret': secret, 'settings': {
                    'server_url': f'https://auth.{env["DOMAIN"]}/application/o/{spec["slug"]}/.well-known/openid-configuration',
                    'token_auth_method': 'client_secret_post'}}], 'SCOPE': ['openid', 'profile', 'email', 'groups']}}
            private_write(stack.path / 'secrets' / 'paperless_socialaccount_providers', json.dumps(config))
    elif spec['type'] == 'saml':
        cert = (stack.path / 'secrets' / 'partdb_saml_sp_certificate').read_text()
        verification = auth.ensure('crypto/certificatekeypairs/', {'name': 'stack-manager:partdb-sp'}, {'certificate_data': cert})
        mapping = auth.ensure('propertymappings/provider/saml/', {'name': 'stack-manager:partdb-groups'}, {
            'saml_name': 'group', 'expression': 'return list(request.user.groups.filter(name__in=' + repr(stack.groups) + ').values_list("name", flat=True))'})
        username = next((m for m in auth.items('propertymappings/provider/saml/') if m.get('managed') == 'goauthentik.io/providers/saml/username'), None)
        if username is None:
            raise ManagerError('SAML-Username-Mapping fehlt.')
        provider = auth.ensure('providers/saml/', {'name': 'stack-manager:' + spec['slug']}, {
            **common, 'acs_url': url + spec['acs'], 'audience': url + spec['audience'],
            'sls_url': url + '/logout', 'sls_binding': 'post', 'sp_binding': 'post',
            'signing_kp': key['pk'], 'verification_kp': verification['pk'],
            'sign_assertion': True, 'sign_response': True, 'sign_logout_request': False, 'sign_logout_response': False,
            'property_mappings': [mapping['pk']], 'name_id_mapping': username['pk']})
        # API returns public certificate at a dedicated endpoint on supported versions.
        pem = auth.docker.exec('core', 'authentik-server', 'ak', 'shell', '-c',
            'from authentik.crypto.models import CertificateKeyPair; print(CertificateKeyPair.objects.get(name="authentik Self-signed Certificate").certificate_data)')
        match = re.search(r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----', pem, re.S)
        if not match:
            raise ManagerError('Authentik-Signaturzertifikat konnte nicht exportiert werden.')
        private_write(stack.path / 'secrets' / 'authentik_saml_idp_certificate', match[0] + '\n')
    else:
        raise ManagerError('Unbekanntes SSO-Verfahren.')
    auth.application(stack, spec['slug'], app['title'] + ' SSO', provider['pk'], url,
                     [groups[g] for g in app['groups']], app.get('icon'))
