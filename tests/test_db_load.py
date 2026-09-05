import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = PROJECT_ROOT / "database" / "load_data.py"


spec = importlib.util.spec_from_file_location("database_load_data", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_loader_exports_and_uses_processed_data():
    assert hasattr(module, "load_library_data")
    assert hasattr(module, "connect_database")
    assert module.PROCESSED_PARQUET.exists()
