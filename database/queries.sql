-- =====================================================
-- LibraSight Database Analytics Queries
-- =====================================================

-- 1. Library Overview
-- Total transactions
SELECT COUNT(*) AS total_transactions
FROM fact_library_transaction;

-- Unique readers
SELECT COUNT(DISTINCT reader_key) AS unique_readers
FROM fact_library_transaction;

-- Unique books
SELECT COUNT(DISTINCT book_key) AS unique_books
FROM fact_library_transaction;

-- Number of branches
SELECT COUNT(*) AS number_of_branches
FROM dim_branch;


-- 2. Books
-- Most borrowed books
SELECT b.book_id,
       b.book_title,
       b.author,
       COUNT(f.transaction_id) AS borrow_count,
       SUM(f.fine_amount) AS total_fine
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.book_id, b.book_title, b.author
ORDER BY borrow_count DESC, total_fine DESC
LIMIT 10;

-- Most popular authors
SELECT b.author,
       COUNT(f.transaction_id) AS transaction_count
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.author
ORDER BY transaction_count DESC
LIMIT 10;

-- Most popular genres
SELECT b.genre,
       COUNT(f.transaction_id) AS transaction_count,
       ROUND(AVG(f.fine_amount), 2) AS avg_fine
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.genre
ORDER BY transaction_count DESC;


-- 3. Reading Trends
-- Monthly transactions
SELECT EXTRACT(YEAR FROM checkout_date) AS year,
       EXTRACT(MONTH FROM checkout_date) AS month,
       COUNT(*) AS transaction_count
FROM fact_library_transaction
WHERE checkout_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM checkout_date), EXTRACT(MONTH FROM checkout_date)
ORDER BY year, month;

-- Yearly transactions
SELECT EXTRACT(YEAR FROM checkout_date) AS year,
       COUNT(*) AS transaction_count
FROM fact_library_transaction
WHERE checkout_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM checkout_date)
ORDER BY year;

-- Genre trends
SELECT b.genre,
       EXTRACT(YEAR FROM f.checkout_date) AS year,
       COUNT(*) AS transaction_count
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
WHERE f.checkout_date IS NOT NULL
GROUP BY b.genre, EXTRACT(YEAR FROM f.checkout_date)
ORDER BY year, transaction_count DESC;

-- Physical vs digital usage
SELECT b.format,
       COUNT(*) AS transaction_count
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.format
ORDER BY transaction_count DESC;


-- 4. Readers
-- Reader types
SELECT r.reader_type,
       COUNT(f.transaction_id) AS transaction_count,
       ROUND(AVG(f.renewal_count), 2) AS avg_renewals
FROM fact_library_transaction f
JOIN dim_reader r ON r.reader_key = f.reader_key
GROUP BY r.reader_type
ORDER BY transaction_count DESC;

-- Reader activity
SELECT r.reader_id,
       r.reader_name,
       r.reader_type,
       COUNT(f.transaction_id) AS total_transactions,
       SUM(f.fine_amount) AS total_fine
FROM fact_library_transaction f
JOIN dim_reader r ON r.reader_key = f.reader_key
GROUP BY r.reader_id, r.reader_name, r.reader_type
ORDER BY total_transactions DESC, total_fine DESC
LIMIT 20;

-- Reader demographics
SELECT r.gender,
       COUNT(DISTINCT r.reader_id) AS unique_readers,
       COUNT(f.transaction_id) AS transactions,
       ROUND(AVG(r.age), 2) AS avg_age
FROM fact_library_transaction f
JOIN dim_reader r ON r.reader_key = f.reader_key
GROUP BY r.gender
ORDER BY unique_readers DESC;


-- 5. Branches
-- Transactions by branch
SELECT br.branch_id,
       br.branch_name,
       br.city,
       COUNT(f.transaction_id) AS transaction_count,
       ROUND(SUM(f.fine_amount), 2) AS total_fine
FROM fact_library_transaction f
JOIN dim_branch br ON br.branch_key = f.branch_key
GROUP BY br.branch_id, br.branch_name, br.city
ORDER BY transaction_count DESC;

-- Readers by branch
SELECT br.branch_id,
       br.branch_name,
       COUNT(DISTINCT f.reader_key) AS unique_readers,
       COUNT(f.transaction_id) AS transactions
FROM fact_library_transaction f
JOIN dim_branch br ON br.branch_key = f.branch_key
GROUP BY br.branch_id, br.branch_name
ORDER BY unique_readers DESC, transactions DESC;

-- Branch collection demand
SELECT br.branch_id,
       br.branch_name,
       b.genre,
       COUNT(f.transaction_id) AS transaction_count
FROM fact_library_transaction f
JOIN dim_branch br ON br.branch_key = f.branch_key
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY br.branch_id, br.branch_name, b.genre
ORDER BY br.branch_id, transaction_count DESC;


-- 6. Collection
-- High-demand books
SELECT b.book_id,
       b.book_title,
       COUNT(f.transaction_id) AS transaction_count,
       AVG(f.available_copies) AS avg_available_copies
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.book_id, b.book_title
HAVING COUNT(f.transaction_id) >= 1
ORDER BY transaction_count DESC
LIMIT 20;

-- Limited-availability books
SELECT b.book_id,
       b.book_title,
       MIN(f.available_copies) AS min_available_copies,
       AVG(f.available_copies) AS avg_available_copies
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.book_id, b.book_title
ORDER BY min_available_copies ASC
LIMIT 20;

-- Reservation-heavy books
SELECT b.book_id,
       b.book_title,
       SUM(f.reservation_count) AS total_reservations,
       COUNT(f.transaction_id) AS transaction_count
FROM fact_library_transaction f
JOIN dim_book b ON b.book_key = f.book_key
GROUP BY b.book_id, b.book_title
ORDER BY total_reservations DESC
LIMIT 20;


-- 7. Data Quality
-- Missing values
SELECT 'dim_reader' AS table_name, COUNT(*) AS missing_count
FROM dim_reader
WHERE reader_name IS NULL OR age IS NULL OR gender IS NULL
UNION ALL
SELECT 'dim_book', COUNT(*)
FROM dim_book
WHERE book_title IS NULL OR author IS NULL OR genre IS NULL
UNION ALL
SELECT 'dim_branch', COUNT(*)
FROM dim_branch
WHERE branch_name IS NULL OR city IS NULL
UNION ALL
SELECT 'fact_library_transaction', COUNT(*)
FROM fact_library_transaction
WHERE transaction_id IS NULL OR checkout_date IS NULL OR due_date IS NULL;

-- Invalid records
SELECT COUNT(*) AS invalid_records
FROM fact_library_transaction
WHERE due_date < checkout_date
   OR return_date < checkout_date
   OR available_copies < 0
   OR fine_amount < 0
   OR age < 0;

-- Duplicate records
SELECT COUNT(*) AS duplicate_records
FROM (
    SELECT transaction_id, COUNT(*)
    FROM fact_library_transaction
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
) dup;

-- Quality score
WITH quality_checks AS (
    SELECT COUNT(*) AS total_rows
    FROM fact_library_transaction
),
valid_rows AS (
    SELECT COUNT(*) AS clean_rows
    FROM fact_library_transaction
    WHERE due_date >= checkout_date
      AND (return_date IS NULL OR return_date >= checkout_date)
      AND available_copies >= 0
      AND fine_amount >= 0
),
missing_rows AS (
    SELECT COUNT(*) AS missing_rows
    FROM fact_library_transaction
    WHERE transaction_id IS NULL OR checkout_date IS NULL OR reader_key IS NULL OR book_key IS NULL OR branch_key IS NULL
)
SELECT
    ROUND((clean_rows * 100.0) / total_rows, 2) AS quality_score_percent,
    clean_rows,
    total_rows,
    missing_rows
FROM quality_checks, valid_rows, missing_rows;


-- =====================================================
-- Optional: dashboard-friendly summary query
-- =====================================================
SELECT
    (SELECT COUNT(*) FROM fact_library_transaction) AS total_transactions,
    (SELECT COUNT(DISTINCT reader_key) FROM fact_library_transaction) AS unique_readers,
    (SELECT COUNT(DISTINCT book_key) FROM fact_library_transaction) AS unique_books,
    (SELECT COUNT(*) FROM dim_branch) AS number_of_branches;
