from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas import PaginatedResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db


router = APIRouter()


# ============================================================
# Get All Books (with optional search query)
# ============================================================

@router.get("/", response_model=PaginatedResponse)
def get_books(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None),
    sort_by: str = Query("book_key"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
):
    """Retrieve books with optional search, sorting, and pagination.

    Returns a PaginatedResponse containing the list of books and metadata.
    """
    # Validate sorting parameters
    sortable = {
        "book_key": "b.book_key",
        "book_title": "b.book_title",
        "author": "b.author",
        "genre": "b.genre",
        "publication_year": "b.publication_year",
    }
    if sort_by not in sortable:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid order; must be 'asc' or 'desc'")

    order_clause = f"{sortable[sort_by]} {order.upper()}"

    # Build WHERE clause for search
    where_clause = ""
    params: dict = {}
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        where_clause = """
            WHERE b.book_title ILIKE :p
               OR b.author ILIKE :p
               OR b.isbn ILIKE :p
               OR b.genre ILIKE :p
               OR b.book_id ILIKE :p
        """
        params["p"] = pattern

    # Total count after filters (before pagination)
    count_sql = f"SELECT COUNT(*) FROM dim_book b {where_clause}"
    total = db.execute(text(count_sql), params).scalar()

    # Main query with pagination
    query_sql = f"""
        SELECT
            b.book_key,
            b.book_id,
            b.isbn,
            b.book_title,
            b.author,
            b.genre,
            b.publication_year,
            b.language,
            b.format,
            b.publisher
        FROM dim_book b
        {where_clause}
        ORDER BY {order_clause}
        OFFSET :skip
        LIMIT :limit
    """
    params.update({"skip": skip, "limit": limit})
    rows = db.execute(text(query_sql), params).mappings().all()
    items = [dict(row) for row in rows]
    return {"items": items, "total": total, "skip": skip, "limit": limit}



# ============================================================
# Top 10 Books
# ============================================================

@router.get("/top")
def top_books(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            b.book_key,
            b.book_title,
            b.author,
            b.genre,
            COUNT(f.transaction_key) AS transaction_count

        FROM fact_library_transaction f

        JOIN dim_book b
            ON f.book_key = b.book_key

        GROUP BY
            b.book_key,
            b.book_title,
            b.author,
            b.genre

        ORDER BY
            transaction_count DESC

        LIMIT 10;
    """)

    result = db.execute(query).mappings().all()

    return [dict(row) for row in result]


# ============================================================
# Books by Genre
# ============================================================

@router.get("/genres")
def book_genres(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            genre,
            COUNT(f.transaction_key) AS transaction_count

        FROM dim_book b

        LEFT JOIN fact_library_transaction f
            ON b.book_key = f.book_key

        GROUP BY
            b.genre

        ORDER BY
            transaction_count DESC;
    """)

    result = db.execute(query).mappings().all()

    return [dict(row) for row in result]