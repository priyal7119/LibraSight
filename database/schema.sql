CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    year INTEGER
);

CREATE TABLE IF NOT EXISTS dim_reader (
    reader_key SERIAL PRIMARY KEY,
    reader_id VARCHAR(50) UNIQUE,
    reader_name VARCHAR(255),
    age INTEGER,
    gender VARCHAR(50),
    reader_type VARCHAR(100),
    membership_date DATE,
    home_branch_id VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_book (
    book_key SERIAL PRIMARY KEY,
    book_id VARCHAR(50) UNIQUE,
    isbn VARCHAR(50),
    book_title VARCHAR(255),
    author VARCHAR(255),
    genre VARCHAR(100),
    publication_year INTEGER,
    language VARCHAR(100),
    format VARCHAR(100),
    publisher VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_book (
    book_key SERIAL PRIMARY KEY,
    book_id VARCHAR(50) UNIQUE,
    isbn VARCHAR(50),
    book_title VARCHAR(255),
    author VARCHAR(255),
    genre VARCHAR(100),
    publication_year INTEGER,
    language VARCHAR(100),
    format VARCHAR(100),
    publisher VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS fact_library_transaction (
    transaction_key SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE,

    reader_key INTEGER,
    book_key INTEGER,
    branch_key INTEGER,
    date_key INTEGER,

    checkout_date DATE,
    due_date DATE,
    return_date DATE,

    transaction_status VARCHAR(50),
    renewal_count INTEGER,
    reservation_flag BOOLEAN,
    reservation_count INTEGER,
    checkout_method VARCHAR(100),
    fine_amount NUMERIC(10,2),
    total_copies INTEGER,
    available_copies INTEGER,

    CONSTRAINT fk_fact_reader
        FOREIGN KEY (reader_key)
        REFERENCES dim_reader(reader_key),

    CONSTRAINT fk_fact_book
        FOREIGN KEY (book_key)
        REFERENCES dim_book(book_key),

    CONSTRAINT fk_fact_branch
        FOREIGN KEY (branch_key)
        REFERENCES dim_branch(branch_key),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);