from pathlib import Path

import pandas as pd

import importlib.util


def load_library_spark_job_module():
    module_path = Path(__file__).resolve().parents[1] / "spark" / "jobs" / "library_spark_job.py"
    spec = importlib.util.spec_from_file_location("library_spark_job", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_write_dataframe_to_parquet(tmp_path):
    module = load_library_spark_job_module()

    output_path = tmp_path / "analytics" / "sample.parquet"
    df = pd.DataFrame({"book_id": [1, 2], "transaction_count": [10, 20]})

    module.write_dataframe_to_parquet(df, output_path)

    assert output_path.exists()
    round_trip = pd.read_parquet(output_path)
    assert round_trip.to_dict("records") == df.to_dict("records")
