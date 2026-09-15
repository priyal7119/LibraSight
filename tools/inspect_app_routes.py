import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import importlib
app_mod = importlib.import_module('app.main')
app = getattr(app_mod, 'app')

print('app module file:', app_mod.__file__)
print('routes:')
for r in app.routes:
    if hasattr(r, 'path'):
        print(' ', r.path)

# show routers imported in app.main's globals
print('\napp.main globals keys:')
print([k for k in app_mod.__dict__.keys() if k in ['dashboard','books','readers','branches','reports','collection','data_quality','notifications']])

try:
    import pkgutil
    print('\napp.routers package files:')
    import app.routers as routers_pkg
    for finder, name, ispkg in pkgutil.iter_modules(routers_pkg.__path__):
        print(' ', name)
except Exception as e:
    print('could not list app.routers:', e)
