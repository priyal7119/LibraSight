from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas import PaginatedResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db


router = APIRouter()


# ============================================================
# Get All Branches (with optional search query)
# ============================================================

@router.get("/", response_model=PaginatedResponse)
def get_branches(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None),
    sort_by: str = Query("branch_key"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
):
    """Retrieve branches with optional search, sorting, and pagination.

    Returns a PaginatedResponse.
    """
    sortable = {
        "branch_key": "b.branch_key",
        "branch_id": "b.branch_id",
        "branch_name": "b.branch_name",
        "city": "b.city",
        "area": "b.area",
        "library_type": "b.library_type",
        "branch_capacity": "b.branch_capacity",
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
            WHERE b.branch_name ILIKE :p
               OR b.city ILIKE :p
               OR b.area ILIKE :p
               OR b.library_type ILIKE :p
               OR b.branch_id ILIKE :p
        """
        params["p"] = pattern

    count_sql = f"SELECT COUNT(*) FROM dim_branch b {where_clause}"
    total = db.execute(text(count_sql), params).scalar()

    query_sql = f"""
        SELECT
            b.branch_key,
            b.branch_id,
            b.branch_name,
            b.city,
            b.area,
            b.library_type,
            b.branch_capacity
        FROM dim_branch b
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
# Branch Performance
# ============================================================

@router.get("/performance")
def branch_performance(
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            b.branch_key,
            b.branch_id,
            b.branch_name,
            b.city,
            COUNT(f.transaction_key) AS transaction_count,
            COALESCE(SUM(f.fine_amount), 0) AS total_fine

        FROM fact_library_transaction f

        JOIN dim_branch b
            ON f.branch_key = b.branch_key

        GROUP BY
            b.branch_key,
            b.branch_id,
            b.branch_name,
            b.city

        ORDER BY
            transaction_count DESC,
            total_fine DESC;
    """)

    result = db.execute(query).mappings().all()

    return [dict(row) for row in result]