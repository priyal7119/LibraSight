# Table Descriptions

This document lists the five main warehouse tables and their columns. Column names and types are taken from `database/schema.sql` and SQLAlchemy models in `backend/app/models.py`.

1) dim_date

- Purpose: Date dimension for transaction checkout dates.
- Columns:
  - `date_key` (INTEGER, PK): surrogate key (YYYYMMDD integer)
  - `full_date` (DATE, UNIQUE, NOT NULL)
  - `day` (INTEGER)
  - `month` (INTEGER)
  - `month_name` (VARCHAR)
  - `quarter` (INTEGER)
  - `year` (INTEGER)

2) dim_reader

- Purpose: Reader (customer) dimension.
- Columns:
  - `reader_key` (SERIAL/INTEGER, PK)
  - `reader_id` (VARCHAR, UNIQUE): natural/business identifier
  - `reader_name` (VARCHAR)
  - `age` (INTEGER)
  - `gender` (VARCHAR)
  - `reader_type` (VARCHAR)
  - `membership_date` (DATE)
  - `home_branch_id` (VARCHAR)

3) dim_book

- Purpose: Book/item dimension.
- Columns:
  - `book_key` (SERIAL/INTEGER, PK)
  - `book_id` (VARCHAR, UNIQUE)
  - `isbn` (VARCHAR)
  - `book_title` (VARCHAR)
  - `author` (VARCHAR)
  - `genre` (VARCHAR)
  - `publication_year` (INTEGER)
  - `language` (VARCHAR)
  - `format` (VARCHAR)
  - `publisher` (VARCHAR)

4) dim_branch

- Purpose: Branch/location dimension.
- Columns (from `backend/app/models.py` and `database/load_data.py`):
  - `branch_key` (INTEGER, PK)
  - `branch_id` (VARCHAR)
  - `branch_name` (VARCHAR)
  - `city` (VARCHAR)
  - `area` (VARCHAR)
  - `library_type` (VARCHAR)
  - `branch_capacity` (INTEGER)

5) fact_library_transaction

- Purpose: Central fact table storing each library transaction.
- Columns:
  - `transaction_key` (SERIAL/INTEGER, PK)
  - `transaction_id` (VARCHAR, UNIQUE)
  - `reader_key` (INTEGER, FK -> dim_reader.reader_key)
  - `book_key` (INTEGER, FK -> dim_book.book_key)
  - `branch_key` (INTEGER, FK -> dim_branch.branch_key)
  - `date_key` (INTEGER, FK -> dim_date.date_key)
  - `checkout_date` (DATE)
  - `due_date` (DATE)
  - `return_date` (DATE)
  - `transaction_status` (VARCHAR)
  - `renewal_count` (INTEGER)
  - `reservation_flag` (BOOLEAN)
  - `reservation_count` (INTEGER)
  - `checkout_method` (VARCHAR)
  - `fine_amount` (NUMERIC(10,2))
  - `total_copies` (INTEGER)
  - `available_copies` (INTEGER)

Important notes

- Column types are those defined in `database/schema.sql` and mirrored by the SQLAlchemy models in `backend/app/models.py`.
- The loader (`database/load_data.py`) expects the cleaned Parquet to contain the natural identifiers (`reader_id`, `book_id`, `branch_id`, `checkout_date`) to map to surrogate keys.
