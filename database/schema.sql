CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    day INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    year INTEGER
);

CREATE TABLE dim_reader (
    reader_key SERIAL PRIMARY KEY,
    reader_id VARCHAR(50) UNIQUE,
    reader_name VARCHAR(100),
    age INTEGER,
    gender VARCHAR(20),
    reader_type VARCHAR(50),
    membership_date DATE,
    home_branch_id VARCHAR(50)
);

CREATE TABLE dim_book (
    book_key SERIAL PRIMARY KEY,
    book_id VARCHAR(50) UNIQUE,
    isbn VARCHAR(30),
    book_title VARCHAR(255),
    author VARCHAR(150),
    genre VARCHAR(100),
    publication_year INTEGER,
    language VARCHAR(50),
    format VARCHAR(50),
    publisher VARCHAR(150)
);

CREATE TABLE dim_branch (
    branch_key SERIAL PRIMARY KEY,
    branch_id VARCHAR(50) UNIQUE,
    branch_name VARCHAR(150),
    city VARCHAR(100),
    area VARCHAR(100),
    library_type VARCHAR(50),
    branch_capacity INTEGER
);

CREATE TABLE fact_library_transaction (
    transaction_key SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE,

    reader_key INTEGER,
    book_key INTEGER,
    branch_key INTEGER,
    date_key INTEGER,

    checkout_date DATE,
    due_date DATE,
    return_date DATE,

    transaction_status VARCHAR(30),

    renewal_count INTEGER DEFAULT 0,

    reservation_flag BOOLEAN DEFAULT FALSE,
    reservation_count INTEGER DEFAULT 0,

    checkout_method VARCHAR(50),

    fine_amount DECIMAL(10,2) DEFAULT 0,

    total_copies INTEGER,
    available_copies INTEGER,

    CONSTRAINT fk_reader
        FOREIGN KEY (reader_key)
        REFERENCES dim_reader(reader_key),

    CONSTRAINT fk_book
        FOREIGN KEY (book_key)
        REFERENCES dim_book(book_key),

    CONSTRAINT fk_branch
        FOREIGN KEY (branch_key)
        REFERENCES dim_branch(branch_key),

    CONSTRAINT fk_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);