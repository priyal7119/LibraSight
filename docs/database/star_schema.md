# Star Schema — LibraSight

The data warehouse follows a star schema: a single wide fact table (`fact_library_transaction`) stores transaction events and references smaller, descriptive dimension tables (`dim_date`, `dim_reader`, `dim_book`, `dim_branch`). This structure optimizes analytical queries and aggregation.

Diagram (logical):

```
              dim_date
                  |
                  |
dim_reader → fact_library_transaction ← dim_book
                  |
                  |
             dim_branch
```

Key concepts

- Fact table: `fact_library_transaction` — stores one row per library transaction (checkout). Contains measures such as `fine_amount`, `renewal_count`, `total_copies`, `available_copies` and foreign keys linking to dimensions.
- Dimensions:
  - `dim_date`: date dimension (surrogate `date_key`, `full_date`, year/month/quarter)
  - `dim_reader`: reader/customer attributes
  - `dim_book`: book attributes (title, author, genre, publication_year)
  - `dim_branch`: branch/location attributes
- Surrogate keys: Each dimension uses a surrogate integer primary key (e.g., `reader_key`, `book_key`). `fact_library_transaction` stores those integer keys as foreign keys for efficient joins and to decouple fact rows from changing natural keys.

Analytical purpose

- The star schema enables fast aggregation by joining the fact table to small dimension tables. Common analyses include transaction trends by date, book popularity, reader segmentation, branch performance, fines, and collection health.
