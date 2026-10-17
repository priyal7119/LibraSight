# LibraSight Viva Preparation Guide

This guide is designed to help you answer viva questions confidently and explain the project in a structured, professional way. It covers the concepts behind the system, how they are implemented in LibraSight, and how to present the project to a professor or evaluator during a live demo.

---

## 1. Problem Statement

### What is the problem?

Library operations generate a large amount of daily transaction data: book checkouts, renewals, returns, branch activity, reader behavior, fine collection, and collection status. This data is usually stored in raw CSV files that are inconsistent, incomplete, and noisy.

The main problem is that raw ticket-level library data is not directly useful for reporting or analytics because it contains:

- missing or invalid values
- duplicate records
- inconsistent date formats
- invalid transaction IDs
- structurally inconsistent records
- business values that do not match expected rules

Without cleaning and validation, the data cannot be trusted for business decisions.

### Why this is a real data engineering problem

A library manager may want to know:

- Which books are most circulated?
- Which branches are performing best?
- Which reader category is most active?
- How many transactions are delayed or penalized with fines?
- Which genres are most popular by month or year?

These questions need a pipeline that can ingest, clean, validate, transform, analyze, and display data in a structured way. That is exactly what LibraSight does.

### How the project addresses the problem

LibraSight creates an end-to-end analytics system where:

1. raw CSV data is ingested
2. data quality checks are performed
3. broken records are rejected
4. clean data is transformed into a consumable format
5. analytics are computed with PySpark
6. a warehouse schema stores structured fact and dimension records
7. a FastAPI backend exposes the data
8. a React frontend visualizes the insights

### Concept behind this problem

This is a classic ETL + BI + analytics pipeline problem.

- ETL stands for Extract, Transform, Load.
- The project extracts raw transaction records, transforms them into valid and standard formats, and loads them into a warehouse-ready structure.
- The analytics layer then turns the cleaned data into operational intelligence.

### How to explain it in viva

Say:

> "The project addresses the challenge of converting messy raw library transaction data into valid, structured, and decision-ready analytics. The raw CSV has quality issues, so the system validates and cleans it before using it for reporting and warehouse storage."

### Demo angle for professor

Open the raw file and show that data is messy, inconsistent, and mixed. Then show the cleaned parquet output, quality reports, and dashboard summaries. This demonstrates the practical value of the pipeline.

---

## 2. Dataset Used

### Dataset name

The project uses the raw library transaction dataset stored at:

- `data/raw/library_raw_data.csv`

### What kind of data is in it?

The dataset contains transaction-level records for a library system. Each row represents a library activity event and includes fields such as:

- transaction id
- reader information
- book metadata
- branch information
- dates such as checkout, due, and return
- transaction status
- reservation and renewal activity
- fine amount
- available and total copies
- collection status

### Why this dataset is suitable

It contains both:

- operational data: transactions and branch behavior
- analytical dimensions: readers, books, branches, dates

This makes it suitable for a star-schema warehouse and multi-dimensional analytics.

### Data quality challenges in the dataset

The dataset is intentionally realistic and not perfectly clean. Typical issues include:

- missing values
- invalid date strings
- duplicate transaction IDs
- bad numeric values
- empty rows
- inconsistent formatting in text columns

This is useful because it shows the real value of validation and transformation.

### Concept behind the dataset usage

The project follows a transactional analytics model where each row is a fact and each dimension is a descriptive entity such as reader, book, date, or branch.

### How to explain in viva

Say:

> "The system is built on a raw library transaction dataset that contains real-world operational inconsistencies. We validate, clean, and structure the data before using it in analytics and dashboard reporting."

### Demo angle for professor

Show:

- the raw data file
- the quality report generated in `data/quality/`
- the rejected records file
- the final processed parquet file in `data/processed/`

This visual chain helps the professor see the full ETL flow.

---

## 3. Tech Stack

LibraSight is built using a modern data-engineering and analytics stack.

### Core technologies

- Python: main language for ETL and processing
- Pandas: data cleaning and validation
- PySpark: large-scale analytics and aggregation
- PostgreSQL: warehouse database
- FastAPI: backend API layer
- React + Vite: frontend dashboard
- Airflow: workflow orchestration
- Docker: containerized local orchestration
- Power BI / reporting artifacts: presentation and analytics export

### Why these tools were chosen

#### Python
Python is used because it provides excellent support for data processing, file handling, validation logic, and ETL pipelines.

#### Pandas
Pandas is used for quick, flexible data cleaning and preprocessing before analytics.

#### PySpark
PySpark is used for distributed-style analytics on large tabular data. It allows operations such as grouping, aggregations, and summary generation across large transaction datasets.

#### PostgreSQL
PostgreSQL is used as the analytics warehouse because it is reliable, structured, and well suited to star schema data models.

#### FastAPI
FastAPI is used to expose data through REST API endpoints for dashboards and reporting.

#### React
The frontend provides an interactive UI for library trends, branch analytics, reader activity, and report views.

#### Airflow
Airflow handles workflow orchestration so the pipeline can run in stages automatically.

### Concept behind the tech stack

This is the standard architecture for an end-to-end data product:

- ingestion layer
- validation layer
- cleaning layer
- analytics layer
- warehouse layer
- API layer
- visualization layer

### How to present it in viva

Say:

> "The project uses a layered architecture where each tool is assigned to a specific responsibility: Python and Pandas handle cleaning, PySpark handles analytics, PostgreSQL stores the warehouse, FastAPI exposes the data, and React presents insights."

### Demo angle

Open the project files and explain which folder corresponds to which layer. Show the backend and frontend separately and explain the flow from raw data to dashboard.

---

## 4. Frontend Run Command and Backend Run Command

### Frontend run command

From the project root:

```powershell
cd .\frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Then open:

```text
http://localhost:5173
```

### Why this works

The frontend is a Vite React app. The command starts a development server that serves the UI and makes API calls to the backend.

### Backend run command

From the project root:

```powershell
cd .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then the backend is available at:

```text
http://localhost:8000
```

You can also check health using:

```text
http://localhost:8000/health
```

### Why the backend matters

The backend acts as the bridge between the warehouse and the frontend. It serves analytics data through REST endpoints such as:

- `/dashboard`
- `/books`
- `/readers`
- `/branches`
- `/reports`
- `/data-quality`

### How to explain this in viva

Say:

> "The frontend is the presentation layer and the backend is the API layer. The frontend requests analytics data from the backend, and the backend queries the PostgreSQL warehouse or serves prepared business summaries."

### Demo angle

Start the backend, then the frontend, open the dashboard, and explain how the page fetches live API data. If asked, show a sample endpoint in the browser or through curl.

---

## 5. Pipeline Structure

The pipeline follows a standard data engineering flow.

### Pipeline stages

1. Raw data ingestion
2. Data validation
3. Data cleaning and transformation
4. Parquet output creation
5. PySpark analytics
6. Data warehouse loading
7. Reporting and dashboard exposure

### Actual logic in the project

The pipeline is implemented across the following modules:

- `ingestion/ingest.py` for raw ingestion
- `validation/validate.py` for data quality checks
- `transformation/clean_transform.py` for cleaning and standardization
- `spark/jobs/library_spark_job.py` for analytics
- `database/load_data.py` for warehouse loading
- `airflow/dags/library_etl_dag.py` for orchestration

### Concept behind the pipeline

This is important because a real data system is never just one script. It is a chain of stages where the output of one stage becomes the input of another. Every stage validates the quality of the system and reduces the chance of downstream errors.

### Demo angle

Explain the flow as:

> Raw CSV -> validate -> clean -> Parquet -> Spark analytics -> warehouse -> API -> dashboard.

This simple explanation is very effective in a viva.

---

## 6. Data Ingestion in Detail

### What is ingestion?

Ingestion is the process of bringing raw data into the system. In this project, the raw data is loaded from a CSV file and prepared for validation.

### Where it happens

- `ingestion/readers.py`
- `ingestion/ingest.py`

### What the ingestion layer does

It:

- identifies the raw dataset location
- checks that the file exists
- reads the CSV with pandas
- verifies basic configuration and required columns
- prepares the dataset for validation and transformation

### Why this is important

If ingestion fails, the rest of the pipeline cannot operate. Good ingestion is the foundation of the entire project.

### In this project specifically

The project reads `data/raw/library_raw_data.csv` and loads it into a pandas DataFrame. This is then used by validation and transformation stages.

### Concept explained

Ingestion is not only reading data; it is also checking whether the dataset is in a usable shape. It acts as the system's entry point.

### How to answer viva questions

Say:

> "Data ingestion is the first layer of the ETL process. It loads the raw library dataset into the system and ensures the file is valid and accessible before any cleaning or analysis occurs."

### Demo angle

Show the raw CSV file and explain the first step of the pipeline in code and execution. If asked, mention that the ingestion step makes sure files and columns are ready for the rest of the process.

---

## 7. Data Cleaning in Detail

### What is data cleaning?

Data cleaning is the process of removing or correcting invalid, duplicate, or inconsistent records so that the dataset is usable for analysis.

### Where it happens

- `transformation/clean_transform.py`

### What the cleaning logic does

The script does the following:

- loads raw data
- checks required columns
- loads rejected records from the quality stage
- removes invalid transaction IDs
- removes exact duplicates
- removes duplicate transactional IDs
- standardizes date values
- normalizes text and number fields
- writes a cleaned dataset to `data/processed/library_clean.parquet`

### Why cleaning is essential

If dirty data enters the warehouse, every report becomes unreliable. Data cleaning ensures that only trustworthy records remain.

### In this project specifically

The cleaning stage reads both:

- the raw dataset
- the rejected records list created during validation

Then it removes any record that failed validation and produces a cleaner dataset ready for analytics.

### Concept explained

This stage converts raw data into a business-ready form. It is the bridge between messy source data and reliable analytics.

### How to explain in viva

Say:

> "The cleaning stage removes bad records and standardizes the dataset so that downstream analytics produces meaningful insights. Without this stage, the final reports would contain noise and incorrect values."

### Demo angle

Show the cleaned parquet output and explain that it is smaller and more reliable than the original CSV. Point out that the rejected records are intentionally removed rather than silently accepted.

---

## 8. Data Validation in Detail

### What is validation?

Validation checks whether the dataset meets the expected structure and rules. It identifies errors before the data is used in the analytics process.

### Where it happens

- `validation/validate.py`

### What is validated

The validation workflow checks:

- expected columns
- duplicate rows
- empty records
- numeric fields such as age, fine amount, copies, branch capacity
- date fields such as membership date and transaction dates
- missing values
- invalid business values

The project uses a helper to parse several date formats such as:

- `YYYY-MM-DD`
- `DD/MM/YYYY`
- `DD-MM-YYYY`
- `DD-Mon-YYYY`

### Generated outputs

The validation process creates reports in:

- `data/quality/data_quality_report.csv`
- `data/quality/rejected_records.csv`

### Why validation matters

Validation is the quality gate of the pipeline. It prevents bad data from entering transformation, analytics, or warehouse storage.

### Concept explained

This is the data quality stage. It ensures the data is structurally and semantically sound.

### How to answer in viva

Say:

> "Validation is performed before cleaning so that the system can detect problems early. It checks both structural integrity and value-level correctness. This helps identify what must be removed or corrected before analytics."

### Demo angle

Show the quality report and explain how it flags issues such as missing values, duplicates, and bad date formats. This shows that the project understands real-world data challenges.

---

## 9. Data Transformation in Detail

### What is transformation?

Transformation is the process of converting raw data into a normalized format suitable for analytics and warehouse ingestion.

### Where it happens

- `transformation/clean_transform.py`

### What transformation includes

This stage includes:

- ensuring required columns are present
- reading rejected IDs from validation output
- removing invalid records
- removing exact duplicates
- deduplicating transaction IDs based on business keys
- converting data to consistent types
- preparing cleaned records for warehouse storage

### Why transformation matters

A raw CSV is not directly warehouse-ready. It must be shaped into a consistent and normalized dataset before it can be loaded into a star schema.

### Concept explained

Transformation is the stage where data becomes consistent, clean, and analytical. It is not just cleaning; it also changes the structure and format of the data so that analysis can happen reliably.

### How to present it in viva

Say:

> "Transformation turns the raw dataset into a business-ready dataset. This includes standardizing values and removing records that were flagged as invalid. The goal is to make the data ready for warehouse loading and analytics."

### Demo angle

Explain that the final cleaned dataset is saved as Parquet and is the canonical input for the Spark analytics job. That makes the connection between cleaning and analytics very clear.

---

## 10. PySpark Analytics

### What is PySpark?

PySpark is the Python API for Apache Spark. It is used to process large tabular datasets efficiently using distributed computing concepts.

### Where it is used

- `spark/jobs/library_spark_job.py`

### What the analytics job does

The Spark job:

- creates a SparkSession
- reads the cleaned Parquet dataset
- prints the schema and sample records
- performs analytical grouping by:
  - book
  - genre
  - reader type
  - branch
  - time trends
- computes metrics such as:
  - count of transactions
  - total fine amount
  - average renewals
  - fine averages by genre
  - transaction counts by branch and city
- writes output into the `spark/output/` directory

### Example analyses in the project

- book-level analytics
- genre-level analytics
- reader-type analytics
- branch and city analytics
- monthly and yearly trends
- collection-level insights

### Concept explained

This is the analytics layer: using SQL-like grouping and aggregate functions to extract business insights from processed data.

### How to respond in viva

Say:

> "PySpark is used to analyze a cleaned transactional dataset. It groups the data by dimensions like books, branches, and reader types and computes aggregate metrics such as transaction counts, average renewals, and total fines."

### Demo angle

Show the output from the Spark script in the terminal and explain that it produces analytical summaries that can later be embedded in reports or APIs.

---

## 11. Warehouse Structure - Dimension Tables and Fact

### What is a data warehouse?

A data warehouse is a structured storage layer designed for analytical reporting and business intelligence. It organizes data in a way that supports efficient querying and aggregated analysis.

### The project uses a star schema

A star schema has one fact table and several related dimension tables.

### Dimension tables

The project includes dimensions such as:

#### `dim_date`
Stores date-related attributes:

- date_key
- full_date
- day
- month
- month_name
- quarter
- year

#### `dim_reader`
Stores reader information:

- reader_id
- reader_name
- age
- gender
- reader_type
- membership_date
- home_branch_id

#### `dim_book`
Stores book metadata:

- book_id
- isbn
- book_title
- author
- genre
- publication_year
- language
- format
- publisher

#### `dim_branch`
Stores branch metadata:

- branch_id
- branch_name
- city
- area
- library_type
- branch_capacity

### Fact table

#### `fact_library_transaction`
This is the central business transaction table. It stores operational details and links to dimension tables via surrogate keys:

- transaction_id
- reader_key
- book_key
- branch_key
- date_key
- checkout_date
- due_date
- return_date
- transaction_status
- renewal_count
- reservation_flag
- reservation_count
- checkout_method
- fine_amount
- total_copies
- available_copies

### Why this is useful

It allows business queries like:

- total transactions by branch
- average renewal count by reader type
- fine amount by genre
- monthly patterns by year
- book circulation by date

### Concept explained

The fact table contains measurable business events, while the dimensions provide descriptive context. This enables efficient analytical queries without redundancy.

### How to explain in viva

Say:

> "The warehouse is designed in a star schema. The fact table stores the transaction events, and the dimension tables provide context like reader, book, date, and branch. This is a standard business-intelligence design used for reporting." 

### Demo angle

If asked, explain how a single transaction connects to a book dimension, a reader dimension, a branch dimension, and a date dimension. This shows your understanding of dimensional modeling.

---

## 12. Repo Structure

The repository is organized into functional layers.

```text
LibraSight/
├── airflow/
│   ├── config/
│   ├── dags/
│   └── logs/
├── backend/
│   ├── app/
│   └── requirements.txt
├── data/
│   ├── processed/
│   ├── quality/
│   └── raw/
├── database/
│   ├── load_data.py
│   ├── queries.sql
│   └── schema.sql
├── docs/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── ingestion/
├── powerbi/
├── reports/
├── spark/
│   ├── jobs/
│   └── output/
├── tests/
├── transformation/
├── validation/
├── tools/
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── ...
```

### How to explain repo structure in viva

Each folder has a purpose:

- `data/`: input and output datasets
- `ingestion/`: raw data import
- `validation/`: checks and quality reports
- `transformation/`: normalization and cleaning
- `spark/`: analytics processing
- `database/`: schema and warehouse loader
- `backend/`: API service
- `frontend/`: UI dashboard
- `airflow/`: orchestration

### Demo angle

Walk the professor through the repo structure and point to the key modules. This shows you understand how the project is organized and how each layer communicates.

---

## 13. Schema Structure

### Where the schema is defined

- `database/schema.sql`

### Main schema concepts

The schema is designed around a star model with fact and dimension tables.

### Dimension schema details

#### `dim_date`
Purpose: time dimension for date-based analysis.

#### `dim_reader`
Purpose: captures reader identity and member profile.

#### `dim_book`
Purpose: stores catalog-level metadata.

#### `dim_branch`
Purpose: stores branch operational context.

### Fact schema details

#### `fact_library_transaction`
Purpose: stores the actual library transactions as measurable events.

### Why this structure is correct for the project

Because the business questions are mostly analytical and time-based:

- Which branches have the most transactions?
- Which books are checked out more often?
- Which reader groups renew books more?
- What is the monthly trend by year?

A star schema is efficient for this kind of reporting.

### Concept explained

This is the database design layer. It ensures the data is organized for analytics rather than for transactional operational storage.

### How to answer viva questions

Say:

> "The database schema is designed for analytics. The fact table stores events, and the dimension tables add context, allowing efficient queries and clear reporting." 

### Demo angle

Open the SQL file and describe one dimension and one fact table. Explain how surrogate keys connect them and why this design supports dashboards and BI workloads.

---

## 14. Orchestration and Airflow

### What is orchestration?

Orchestration is the automated management of the sequence of tasks in a pipeline. In this project, Airflow orchestrates the entire ETL and analytics workflow.

### Where it is configured

- `airflow/dags/library_etl_dag.py`
- `docker-compose.yml`
- `Dockerfile`

### Airflow DAG flow

The pipeline defined in the DAG executes in the following order:

1. `ingest_data`
2. `validate_data`
3. `clean_transform`
4. `save_parquet`
5. `spark_processing`
6. `load_postgresql`
7. `quality_check`

This sequence ensures that each step waits for the previous step to complete successfully.

### Why orchestration is important

Without orchestration, each ETL task has to be run manually. Airflow provides:

- scheduled execution
- dependency management
- task chaining
- workflow visibility
- failure handling and logs

### Concept explained

Airflow turns a manual script-based process into a managed workflow. It makes the project more reliable and easier to monitor.

### How to run the workflow

From the project root:

```powershell
docker compose up --build
```

Then open the Airflow UI at:

```text
http://localhost:8080
```

Trigger the DAG named:

```text
library_etl_pipeline
```

### How to explain in viva

Say:

> "Airflow is used to automate the complete ETL lifecycle. It controls the order of ingestion, validation, cleaning, analytics, warehouse loading, and final quality checks. This is important because in a real data pipeline, tasks must follow a dependency chain and be monitored as a workflow."

### Demo angle

Open the Airflow UI and show the DAG graph. Explain each task and their sequence. This is one of the strongest visual demonstrations of the project’s engineering depth.

---

## Final Viva Summary

LibraSight is a complete end-to-end library analytics project that demonstrates:

- data ingestion from raw CSV files
- structured validation and quality checking
- cleaning and transformation logic
- analytics using PySpark
- a star-schema warehouse design
- API-based access through FastAPI
- dashboard visualization through React
- workflow orchestration with Airflow

The project is valuable because it mimics a real-world data engineering system where raw operational data becomes trusted business intelligence.

### 30-second viva answer

> "LibraSight is a library analytics project built to transform raw library transaction data into structured, validated, and meaningful business insights. It ingests a raw CSV, validates and cleans the records, processes the data with PySpark, loads it into a star-schema warehouse, exposes it through a FastAPI backend, and presents it in a React dashboard. Airflow orchestrates the full pipeline, making it a complete ETL and analytics solution."

### Best demo flow for a professor

1. Start the backend.
2. Start the frontend.
3. Open the Airflow UI.
4. Show the DAG graph.
5. Show the raw dataset.
6. Explain validation and quality reports.
7. Show the cleaned parquet output.
8. Explain the star schema.
9. Display the dashboard analytics.
10. Conclude by saying the project solves a real business problem in a structured engineering way.

This flow is simple, professional, and convincing during a viva or project presentation.
