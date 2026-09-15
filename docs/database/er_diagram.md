# ER Diagram — LibraSight Star Schema

The warehouse implements a star schema with one central fact table and four dimension tables.

Entities (tables):

- `dim_date`
- `dim_reader`
- `dim_book`
- `dim_branch`
- `fact_library_transaction`

Mermaid ER diagram (simplified):

```mermaid
erDiagram
    DIM_DATE {
        INTEGER date_key PK
        DATE full_date
    }
    DIM_READER {
        INTEGER reader_key PK
        VARCHAR reader_id
    }
    DIM_BOOK {
        INTEGER book_key PK
        VARCHAR book_id
    }
    DIM_BRANCH {
        INTEGER branch_key PK
        VARCHAR branch_id
    }
    FACT_LIBRARY_TRANSACTION {
        INTEGER transaction_key PK
        VARCHAR transaction_id
        INTEGER reader_key FK
        INTEGER book_key FK
        INTEGER branch_key FK
        INTEGER date_key FK
    }

    DIM_DATE ||--o{ FACT_LIBRARY_TRANSACTION : "date_key"
    DIM_READER ||--o{ FACT_LIBRARY_TRANSACTION : "reader_key"
    DIM_BOOK ||--o{ FACT_LIBRARY_TRANSACTION : "book_key"
    DIM_BRANCH ||--o{ FACT_LIBRARY_TRANSACTION : "branch_key"
```

Primary keys, foreign keys and cardinality are described in the `relationships.md` and `table_descriptions.md` documents.
