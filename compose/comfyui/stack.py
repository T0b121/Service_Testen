AUTH_GROUPS = ['comfyui-admins', 'comfyui-users']

TITLE = 'comfyui'
REQUIRES = ['core']
APPLICATIONS = [{'groups': ['comfyui-users', 'comfyui-admins'],
  'icon': 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/comfyui.png',
  'routers': ['comfyui'],
  'slug': 'comfyui',
  'title': 'comfyui'}]
