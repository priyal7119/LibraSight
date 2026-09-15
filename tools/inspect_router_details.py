import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import importlib
app_mod = importlib.import_module('app.main')
print('app module file:', app_mod.__file__)

for name in ['dashboard','books','readers','branches','reports','collection','data_quality','notifications']:
    mod = importlib.import_module('app.routers.'+name)
    has_router = hasattr(mod, 'router')
    print(f"module app.routers.{name}: has router: {has_router}")
    if has_router:
        router = getattr(mod, 'router')
        try:
            print('  router routes:')
            for r in router.routes:
                path = getattr(r, 'path', None)
                print('   ', path)
        except Exception as e:
            print('  could not list router.routes:', e)

print('\napp registered routes:')
for r in app_mod.app.routes:
    print(' ', getattr(r,'path',None))
