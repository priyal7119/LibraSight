from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas import PaginatedResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db


router = APIRouter()


# ============================================================
# Get All Readers (with optional search query)
# ============================================================

@router.get("/", response_model=PaginatedResponse)
def get_readers(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None),
    sort_by: str = Query("reader_key"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
):
    """Retrieve readers with optional search, sorting, and pagination.

    Returns a PaginatedResponse.
    """
    sortable = {
        "reader_key": "r.reader_key",
        "reader_id": "r.reader_id",
        "reader_name": "r.reader_name",
        "age": "r.age",
        "gender": "r.gender",
        "reader_type": "r.reader_type",
        "membership_date": "r.membership_date",
    }
    if sort_by not in sortable:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="Invalid order; must be 'asc' or 'desc'")

    order_clause = f"{sortable[sort_by]} {order.upper()}"

    where_clause = ""
    params: dict = {}
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        where_clause = """
            WHERE r.reader_name ILIKE :p
               OR r.reader_id ILIKE :p
               OR r.gender ILIKE :p
               OR r.reader_type ILIKE :p
               OR r.home_branch_id ILIKE :p
        """
        params["p"] = pattern

    count_sql = f"SELECT COUNT(*) FROM dim_reader r {where_clause}"
    total = db.execute(text(count_sql), params).scalar()

    query_sql = f"""
        SELECT
            r.reader_key,
            r.reader_id,
            r.reader_name,
            r.age,
            r.gender,
            r.reader_type,
            r.membership_date,
            r.home_branch_id
        FROM dim_reader r
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
# Reader Types
# ============================================================

@router.get("/types")
def reader_types(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            r.reader_type,
            COUNT(f.transaction_key) AS transaction_count

        FROM dim_reader r

        LEFT JOIN fact_library_transaction f
            ON r.reader_key = f.reader_key

        GROUP BY
            r.reader_type

        ORDER BY
            transaction_count DESC;
    """)

    result = db.execute(query).mappings().all()

    return [dict(row) for row in result]


# ============================================================
# Reader Activity
# ============================================================

@router.get("/activity")
def reader_activity(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            r.reader_key,
            r.reader_id,
            r.reader_name,
            r.reader_type,
            COUNT(f.transaction_key) AS transaction_count,
            COALESCE(SUM(f.fine_amount), 0) AS total_fine

        FROM fact_library_transaction f

        JOIN dim_reader r
            ON f.reader_key = r.reader_key

        GROUP BY
            r.reader_key,
            r.reader_id,
            r.reader_name,
            r.reader_type

        ORDER BY
            transaction_count DESC,
            total_fine DESC;
    """)

    result = db.execute(query).mappings().all()

    return [dict(row) for row in result]