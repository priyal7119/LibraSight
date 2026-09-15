from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.report_service import (
    generate_branch_performance_report,
    generate_collection_analysis_report,
    generate_data_quality_report,
    generate_monthly_performance_report,
    generate_reading_trends_report,
)

router = APIRouter()


def _pdf_response(filename, generator, db):
    path = generator(db)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF report not generated: {path}"
        )

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=path.name,
    )


# ============================================================
# Monthly Performance Report
# ============================================================

@router.get("/monthly-performance")
def monthly_performance_report(
    db: Session = Depends(get_db)
):
    return _pdf_response(
        "monthly_library_performance.pdf",
        generate_monthly_performance_report,
        db,
    )


@router.get("/monthly")
def monthly_report(
    db: Session = Depends(get_db)
):
    return monthly_performance_report(db)


# ============================================================
# Reading Trends Report
# ============================================================

@router.get("/reading-trends")
def reading_trends_report(
    db: Session = Depends(get_db)
):
    return _pdf_response(
        "reading_trends.pdf",
        generate_reading_trends_report,
        db,
    )


# ============================================================
# Collection Analysis Report
# ============================================================

@router.get("/collection-analysis")
def collection_analysis_report(
    db: Session = Depends(get_db)
):
    return _pdf_response(
        "collection_analysis.pdf",
        generate_collection_analysis_report,
        db,
    )


@router.get("/collection")
def collection_report(
    db: Session = Depends(get_db)
):
    return collection_analysis_report(db)


# ============================================================
# Branch Performance Report
# ============================================================

@router.get("/branch-performance")
def branch_performance_report(
    db: Session = Depends(get_db)
):
    return _pdf_response(
        "branch_performance.pdf",
        generate_branch_performance_report,
        db,
    )


@router.get("/branch")
def branch_report(
    db: Session = Depends(get_db)
):
    return branch_performance_report(db)


# ============================================================
# Data Quality Report
# ============================================================

@router.get("/data-quality")
def data_quality_report(
    db: Session = Depends(get_db)
):
    return _pdf_response(
        "data_quality.pdf",
        generate_data_quality_report,
        db,
    )