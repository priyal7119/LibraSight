from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/summary")
def get_collection_summary(db: Session = Depends(get_db)):
    # 1. Summary stats
    stats_query = text("""
        SELECT
            COUNT(*) AS total_transactions,
            ROUND(AVG(available_copies), 2) AS avg_available_copies,
            COUNT(CASE WHEN available_copies = 0 THEN 1 END) AS zero_available_count
        FROM fact_library_transaction;
    """)
    stats = db.execute(stats_query).mappings().one()

    # 2. Low-stock alerts (available_copies = 0)
    low_stock_query = text("""
        SELECT DISTINCT ON (b.book_key)
            b.book_key,
            b.book_id,
            b.book_title,
            b.author,
            b.genre,
            f.available_copies,
            f.total_copies,
            f.reservation_count
        FROM fact_library_transaction f
        JOIN dim_book b ON f.book_key = b.book_key
        WHERE f.available_copies = 0
        ORDER BY b.book_key, f.reservation_count DESC
        LIMIT 15;
    """)
    low_stock_records = db.execute(low_stock_query).mappings().all()

    # 3. Reservation-heavy titles (high demand by total reservations)
    reservation_query = text("""
        SELECT
            b.book_key,
            b.book_id,
            b.book_title,
            b.author,
            b.genre,
            SUM(COALESCE(f.reservation_count, 0)) AS total_reservations,
            COUNT(f.transaction_key) AS transaction_count,
            ROUND(AVG(f.available_copies), 1) AS avg_available
        FROM fact_library_transaction f
        JOIN dim_book b ON f.book_key = b.book_key
        GROUP BY b.book_key, b.book_id, b.book_title, b.author, b.genre
        ORDER BY total_reservations DESC
        LIMIT 10;
    """)
    reservation_records = db.execute(reservation_query).mappings().all()

    return {
        "collection_status": "Healthy",
        "total_transactions": stats["total_transactions"] or 0,
        "avg_available_copies": float(stats["avg_available_copies"] or 0),
        "zero_available_count": stats["zero_available_count"] or 0,
        "low_stock_alerts": [dict(r) for r in low_stock_records],
        "reservation_heavy": [dict(r) for r in reservation_records],
    }
