-- Important SQL queries for LibraSight (non-destructive)

-- Table counts
SELECT COUNT(*) AS dim_date_count FROM dim_date;
SELECT COUNT(*) AS dim_reader_count FROM dim_reader;
SELECT COUNT(*) AS dim_book_count FROM dim_book;
SELECT COUNT(*) AS dim_branch_count FROM dim_branch;
SELECT COUNT(*) AS fact_library_transaction_count FROM fact_library_transaction;

-- Unique transaction check
SELECT COUNT(*) AS total_rows FROM fact_library_transaction;
SELECT COUNT(DISTINCT transaction_id) AS unique_transaction_ids FROM fact_library_transaction;

-- Find duplicate transaction IDs (if any)
SELECT transaction_id, COUNT(*) AS cnt
FROM fact_library_transaction
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- Foreign-key integrity checks (identify invalid foreign keys)
-- Rows in fact where reader_key not present in dim_reader
SELECT f.transaction_key, f.transaction_id
FROM fact_library_transaction f
LEFT JOIN dim_reader r ON f.reader_key = r.reader_key
WHERE r.reader_key IS NULL;

-- Rows in fact where book_key not present in dim_book
SELECT f.transaction_key, f.transaction_id
FROM fact_library_transaction f
LEFT JOIN dim_book b ON f.book_key = b.book_key
WHERE b.book_key IS NULL;

-- Rows in fact where branch_key not present in dim_branch
SELECT f.transaction_key, f.transaction_id
FROM fact_library_transaction f
LEFT JOIN dim_branch br ON f.branch_key = br.branch_key
WHERE br.branch_key IS NULL;

-- Rows in fact where date_key not present in dim_date
SELECT f.transaction_key, f.transaction_id
FROM fact_library_transaction f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;

-- Basic analytical queries
-- Top 10 books by transaction count
SELECT b.book_title, b.author, COUNT(f.transaction_key) AS tx_count
FROM fact_library_transaction f
JOIN dim_book b ON f.book_key = b.book_key
GROUP BY b.book_title, b.author
ORDER BY tx_count DESC
LIMIT 10;

-- Transactions per year
SELECT d.year, COUNT(f.transaction_key) AS tx_count
FROM fact_library_transaction f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year
ORDER BY d.year;

-- Branch performance (transactions and total fines)
SELECT br.branch_id, br.branch_name, COUNT(f.transaction_key) AS tx_count, COALESCE(SUM(f.fine_amount),0) AS total_fines
FROM fact_library_transaction f
JOIN dim_branch br ON f.branch_key = br.branch_key
GROUP BY br.branch_id, br.branch_name
ORDER BY tx_count DESC;
