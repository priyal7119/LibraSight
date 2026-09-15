from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


def _build_filter_clauses(
    year: Optional[int] = None,
    branch_id: Optional[str] = None,
    genre: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """
    Build WHERE clauses and parameter bindings for star schema queries.
    f: fact_library_transaction
    d: dim_date
    br: dim_branch
    b: dim_book
    """
    conditions = []
    params = {}

    if year is not None:
        conditions.append("d.year = :year")
        params["year"] = int(year)

    if branch_id:
        conditions.append("br.branch_id = :branch_id")
        params["branch_id"] = str(branch_id).strip()

    if genre:
        conditions.append("b.genre = :genre")
        params["genre"] = str(genre).strip()

    if start_date:
        conditions.append("f.checkout_date >= :start_date")
        params["start_date"] = start_date

    if end_date:
        conditions.append("f.checkout_date <= :end_date")
        params["end_date"] = end_date

    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where_sql, params


# ============================================================
# Dashboard Summary (Filtered)
# ============================================================

@router.get("/summary")
def dashboard_summary(
    year: Optional[int] = Query(None),
    branch_id: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    where_sql, params = _build_filter_clauses(year, branch_id, genre, start_date, end_date)

    query = text(f"""
        SELECT
            COUNT(f.transaction_key) AS total_transactions,
            COUNT(DISTINCT f.book_key) AS total_books,
            COUNT(DISTINCT f.reader_key) AS total_readers,
            COUNT(DISTINCT f.branch_key) AS total_branches
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql};
    """)

    result = db.execute(query, params).mappings().one()
    return dict(result)


# ============================================================
# Monthly Transaction Trends (Filtered)
# ============================================================

@router.get("/trends")
def dashboard_trends(
    year: Optional[int] = Query(None),
    branch_id: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    where_sql, params = _build_filter_clauses(year, branch_id, genre, start_date, end_date)

    query = text(f"""
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(f.transaction_key) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month;
    """)

    result = db.execute(query, params).mappings().all()
    return [dict(row) for row in result]


# ============================================================
# Transaction Status (Filtered)
# ============================================================

@router.get("/status")
def dashboard_status(
    year: Optional[int] = Query(None),
    branch_id: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    where_sql, params = _build_filter_clauses(year, branch_id, genre, start_date, end_date)

    query = text(f"""
        SELECT
            f.transaction_status AS status,
            COUNT(f.transaction_key) AS count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY f.transaction_status
        ORDER BY count DESC;
    """)

    result = db.execute(query, params).mappings().all()
    return [dict(row) for row in result]


# ============================================================
# Expanded Analytics (Filtered)
# ============================================================

@router.get("/analytics")
def dashboard_analytics(
    year: Optional[int] = Query(None),
    branch_id: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    where_sql, params = _build_filter_clauses(year, branch_id, genre, start_date, end_date)

    # 1. Checkout Methods
    method_query = text(f"""
        SELECT
            f.checkout_method,
            COUNT(f.transaction_key) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY f.checkout_method
        ORDER BY transaction_count DESC;
    """)
    methods = [dict(r) for r in db.execute(method_query, params).mappings().all()]

    # 2. Reservation Summary
    res_query = text(f"""
        SELECT
            COALESCE(SUM(f.reservation_count), 0) AS total_reservations,
            COUNT(CASE WHEN f.reservation_flag THEN 1 END) AS transactions_with_reservations,
            COUNT(f.transaction_key) AS total_transactions
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql};
    """)
    res_summary = dict(db.execute(res_query, params).mappings().one())

    # 3. Fine Trend
    fine_query = text(f"""
        SELECT
            d.year,
            d.month,
            d.month_name,
            COALESCE(SUM(f.fine_amount), 0) AS total_fine
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month;
    """)
    fine_trend = [dict(r) for r in db.execute(fine_query, params).mappings().all()]

    # 4. Collection Health Aggregates
    coll_query = text(f"""
        SELECT
            COALESCE(SUM(f.total_copies), 0) AS total_copies,
            COALESCE(SUM(f.available_copies), 0) AS available_copies,
            ROUND(AVG(f.available_copies), 2) AS avg_available_copies,
            COUNT(CASE WHEN f.available_copies = 0 THEN 1 END) AS zero_available_count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql};
    """)
    coll_health = dict(db.execute(coll_query, params).mappings().one())
    total_c = coll_health.get("total_copies") or 0
    avail_c = coll_health.get("available_copies") or 0
    coll_health["unavailable_copies"] = max(0, total_c - avail_c)
    if coll_health.get("avg_available_copies") is not None:
        coll_health["avg_available_copies"] = float(coll_health["avg_available_copies"])
    else:
        coll_health["avg_available_copies"] = 0.0

    # 5. Transactions by Genre (Filtered)
    genre_query = text(f"""
        SELECT
            b.genre,
            COUNT(f.transaction_key) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY b.genre
        ORDER BY transaction_count DESC;
    """)
    genres = [dict(r) for r in db.execute(genre_query, params).mappings().all()]

    # 6. Branch Performance (Filtered)
    branch_query = text(f"""
        SELECT
            br.branch_id,
            br.branch_name,
            COUNT(f.transaction_key) AS transaction_count,
            COALESCE(SUM(f.fine_amount), 0) AS total_fine
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY br.branch_id, br.branch_name
        ORDER BY transaction_count DESC;
    """)
    branches = [dict(r) for r in db.execute(branch_query, params).mappings().all()]

    # 7. Reader Types (Filtered)
    reader_query = text(f"""
        SELECT
            r.reader_type,
            COUNT(f.transaction_key) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        JOIN dim_reader r ON f.reader_key = r.reader_key
        {where_sql}
        GROUP BY r.reader_type
        ORDER BY transaction_count DESC;
    """)
    reader_types = [dict(r) for r in db.execute(reader_query, params).mappings().all()]

    # 8. Top 5 Books (Filtered)
    top_books_query = text(f"""
        SELECT
            b.book_key,
            b.book_title,
            b.author,
            b.genre,
            COUNT(f.transaction_key) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_branch br ON f.branch_key = br.branch_key
        JOIN dim_book b ON f.book_key = b.book_key
        {where_sql}
        GROUP BY b.book_key, b.book_title, b.author, b.genre
        ORDER BY transaction_count DESC
        LIMIT 5;
    """)
    top_books = [dict(r) for r in db.execute(top_books_query, params).mappings().all()]

    return {
        "checkout_methods": methods,
        "reservation_summary": res_summary,
        "fine_trend": fine_trend,
        "collection_health": coll_health,
        "genres": genres,
        "branches": branches,
        "reader_types": reader_types,
        "top_books": top_books,
    }


# ============================================================
# Filter Options (Years, etc.)
# ============================================================

@router.get("/years")
def get_filter_years(db: Session = Depends(get_db)):
    query = text("""
        SELECT DISTINCT d.year
        FROM fact_library_transaction f
        JOIN dim_date d ON f.date_key = d.date_key
        ORDER BY d.year;
    """)
    years = [r[0] for r in db.execute(query).all()]
    return years


# ============================================================
# Global Unified Search (Books, Readers, Branches)
# ============================================================

@router.get("/search")
def global_search(
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if not q or not q.strip():
        return {
            "query": "",
            "books": [],
            "readers": [],
            "branches": [],
            "total_matches": 0,
        }

    pattern = f"%{q.strip()}%"

    # Search books in PostgreSQL
    books_query = text("""
        SELECT book_id, book_title, author, genre, publication_year
        FROM dim_book
        WHERE book_title ILIKE :q
           OR author ILIKE :q
           OR genre ILIKE :q
           OR isbn ILIKE :q
        ORDER BY book_title
        LIMIT 6;
    """)
    books = [dict(r) for r in db.execute(books_query, {"q": pattern}).mappings().all()]

    # Search readers in PostgreSQL
    readers_query = text("""
        SELECT reader_id, reader_name, reader_type, home_branch_id
        FROM dim_reader
        WHERE reader_name ILIKE :q
           OR reader_id ILIKE :q
           OR reader_type ILIKE :q
        ORDER BY reader_name
        LIMIT 6;
    """)
    readers = [dict(r) for r in db.execute(readers_query, {"q": pattern}).mappings().all()]

    # Search branches in PostgreSQL
    branches_query = text("""
        SELECT branch_id, branch_name, city, area, library_type
        FROM dim_branch
        WHERE branch_name ILIKE :q
           OR city ILIKE :q
           OR area ILIKE :q
           OR branch_id ILIKE :q
        ORDER BY branch_name
        LIMIT 6;
    """)
    branches = [dict(r) for r in db.execute(branches_query, {"q": pattern}).mappings().all()]

    total = len(books) + len(readers) + len(branches)

    return {
        "query": q.strip(),
        "books": books,
        "readers": readers,
        "branches": branches,
        "total_matches": total,
    }