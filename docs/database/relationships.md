# Relationships

This document describes the primary relationships between the dimension tables and the fact table.

1) dim_date.date_key → fact_library_transaction.date_key

- Primary key: `dim_date.date_key` (INTEGER)
- Foreign key: `fact_library_transaction.date_key` (INTEGER)
- Cardinality: `dim_date` 1 ─── * `fact_library_transaction` (many transactions occur on the same date)
- Direction: dim_date → fact_library_transaction (dimension to fact)

2) dim_reader.reader_key → fact_library_transaction.reader_key

- Primary key: `dim_reader.reader_key` (INTEGER)
- Foreign key: `fact_library_transaction.reader_key` (INTEGER)
- Cardinality: `dim_reader` 1 ─── * `fact_library_transaction` (one reader can have many transactions)
- Direction: dim_reader → fact_library_transaction

3) dim_book.book_key → fact_library_transaction.book_key

- Primary key: `dim_book.book_key` (INTEGER)
- Foreign key: `fact_library_transaction.book_key` (INTEGER)
- Cardinality: `dim_book` 1 ─── * `fact_library_transaction` (one book can appear in many transactions)
- Direction: dim_book → fact_library_transaction

4) dim_branch.branch_key → fact_library_transaction.branch_key

- Primary key: `dim_branch.branch_key` (INTEGER)
- Foreign key: `fact_library_transaction.branch_key` (INTEGER)
- Cardinality: `dim_branch` 1 ─── * `fact_library_transaction` (one branch services many transactions)
- Direction: dim_branch → fact_library_transaction

Notes

- All relationships are implemented as foreign key constraints in `database/schema.sql` and enforced by the loader in `database/load_data.py`.
