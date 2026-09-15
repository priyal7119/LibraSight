# LibraSight

LibraSight is a library analytics and data engineering project built to ingest raw circulation data, validate quality issues, clean and transform the records, generate analytical outputs, and expose business insights through a FastAPI backend and React dashboard.

## Project purpose

The platform is designed for library operations teams and analysts who need to understand:

- circulation trends
- reader behavior and library usage
- branch performance
- collection health and availability
- data-quality issues across source records

The solution combines ETL, warehouse loading, reporting, and visualization into a single end-to-end project for local analytics and demonstration workflows.

## Current project scope

This repository contains the following major components:

- `ingestion/` — raw data ingestion and schema/input handling
- `validation/` — rule-based validation, rejected-record handling, and data-quality reporting
- `transformation/` — cleaning, normalization, and parquet export logic
- `spark/` — PySpark aggregation jobs and generated analytical outputs
- `database/` — SQL schema and warehouse loading scripts
- `backend/` — FastAPI application and endpoint layer
- `frontend/` — Vite + React dashboard UI
- `airflow/` — orchestration DAG for ETL workflow execution
- `data/` — raw, processed, and quality output files
- `tests/` — automated validation for API, data extraction, transformation, Spark jobs, and reports

## Technology stack

- Python 3.11+
- Pandas, NumPy, PyArrow
- PySpark 4.2.0
- SQLAlchemy + PostgreSQL
- FastAPI + Uvicorn
- React 18 + Vite
- Apache Airflow 3.3.1
- Docker + Docker Compose
- ReportLab, PyPDF, Matplotlib

## High-level architecture

```mermaid
flowchart LR
    RAW[Raw library CSV] --> INGEST[Ingestion]
    INGEST --> VALIDATE[Validation]
    VALIDATE --> CLEAN[Transformation]
    CLEAN --> PARQUET[Processed parquet data]
    PARQUET --> SPARK[PySpark analytics]
    SPARK --> DB[PostgreSQL star schema]
    DB --> API[FastAPI API]
    API --> UI[React dashboard]
```

## Workflow summary

1. Raw library records are ingested from source files.
2. Validation checks identify structural, numeric, date, missing-value, range, and logical integrity issues.
3. Cleaned data is transformed and exported for downstream analysis.
4. PySpark jobs aggregate the processed data into analytical outputs.
5. Results are loaded into a PostgreSQL warehouse structure.
6. The backend exposes analytics endpoints for dashboard and report use.
7. The frontend visualizes trends and operational metrics.

## Data-quality model

The project includes automated validation coverage for:

- structural checks
- duplicate detection
- missing values
- data type integrity
- date validation
- range constraints
- logical consistency checks

Examples from the current validation rules include:

- duplicate records
- age outside 0–120
- invalid publication year
- negative fine amount
- negative available copies
- available copies exceeding total copies
- due or return dates earlier than checkout date

These validation results are written to the data-quality outputs under `data/quality/` and surfaced by the API summary endpoints.

## Operating environment

### Prerequisites

- Python 3.11 or newer
- Node.js 18+
- pip
- Docker + Docker Compose for the Airflow workflow

### Backend setup

From the project root:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install the backend dependencies:

```bash
pip install -r requirements.txt
```

To start the API from the backend folder:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints available include:

- http://localhost:8000
- http://localhost:8000/docs

### Frontend setup

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 4173
```

Frontend UI:

- http://localhost:4173

### Airflow orchestration

The project includes a containerized Airflow DAG for the ETL pipeline:

```bash
docker-compose up --build
```

Airflow UI:

- http://localhost:8080

## Manual ETL execution

The pipeline components can also be run directly from the project root:

```bash
python ingestion/ingest.py
python validation/validate.py
python transformation/clean_transform.py
python spark/jobs/library_spark_job.py
python database/load_data.py
```

Generated outputs are stored in:

- `data/raw/`
- `data/processed/`
- `data/quality/`
- `spark/output/`

## Testing and verification

The project includes pytest-based verification for:

- ETL ingestion and readers
- validation logic
- transformation behavior
- Spark output generation
- PDF and report generation
- API endpoints

Run tests with:

```bash
pytest
```

## Current status

The repository is a working local analytics prototype with a complete data pipeline, validation framework, API layer, and dashboard frontend. It is suitable for local demonstration, project reporting, and further enhancement.

## Notes for reporting and future documentation

This repository is well suited for use as a reference project in technical documentation, business reporting, and project summary materials. The primary technical themes are:

- library data engineering
- dataset quality governance
- analytical warehouse modeling
- operational reporting
- dashboard-based insight delivery

## Contributing

Contributions are welcome. Changes to the pipeline, validation rules, API behavior, or UI should be reflected in tests and relevant documentation.

## License

No root license file is currently present in the repository. This section should be updated when a formal project license is added.
