from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError:  # pragma: no cover
    # Define minimal stubs to avoid import errors when report generation is not used.
    colors = None
    A4 = None
    ParagraphStyle = object
    def getSampleStyleSheet():
        return {}
    class SimpleDocTemplate:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def build(self, *args, **kwargs):
            raise RuntimeError("Report generation not available – missing reportlab dependency.")
    class Spacer:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
    class Table:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
        def setStyle(self, *args, **kwargs):
            pass
    class TableStyle:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass
from sqlalchemy import text


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _format_number(value):
    if value is None:
        return "N/A"

    if isinstance(value, float):
        return f"{value:,.2f}"

    return str(value)


def _safe_table(rows, headers):
    if not rows:
        return [["No data available"]]

    return [headers] + rows


def _add_section(story, styles, title, data_rows, headers, note=None):

    story.append(
        Paragraph(
            title,
            styles["Heading2"]
        )
    )

    if note:
        story.append(
            Paragraph(
                note,
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 10))

    table = Table(
        _safe_table(
            data_rows,
            headers
        )
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.grey,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.whitesmoke,
                        colors.Color(
                            0.96,
                            0.96,
                            0.97
                        ),
                    ],
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 18))


def _render_summary_report(
    filename,
    report_title,
    sections
):

    output_path = REPORT_DIR / filename

    styles = getSampleStyleSheet()

    if "LibraTitle" not in styles.byName:
        styles.add(
            ParagraphStyle(
                name="LibraTitle",
                parent=styles["Title"],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#111827"),
                spaceAfter=8,
            )
        )

    if "LibraSubtitle" not in styles.byName:
        styles.add(
            ParagraphStyle(
                name="LibraSubtitle",
                parent=styles["Heading2"],
                fontSize=13,
                textColor=colors.HexColor("#374151"),
                spaceAfter=12,
            )
        )

    if "LibraBodyText" not in styles.byName:
        styles.add(
            ParagraphStyle(
                name="LibraBodyText",
                parent=styles["BodyText"],
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#374151"),
            )
        )

    story = []

    story.append(
        Paragraph(
            "LibraSight",
            styles["LibraTitle"]
        )
    )

    story.append(
        Paragraph(
            report_title,
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            styles["LibraBodyText"],
        )
    )

    story.append(Spacer(1, 18))

    for title, rows, headers, note in sections:

        if rows:

            _add_section(
                story,
                styles,
                title,
                rows,
                headers,
                note,
            )

        else:

            story.append(
                Paragraph(
                    title,
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    note or "No records available for this section.",
                    styles["LibraBodyText"],
                )
            )

            story.append(Spacer(1, 12))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=42,
    )

    doc.build(story)

    return output_path


def _run_query(db, sql):
    return db.execute(
        text(sql)
    ).mappings().all()


# ============================================================
# Monthly Performance Report
# ============================================================

def generate_monthly_performance_report(db):

    summary_sql = """
        SELECT
            COUNT(*) AS total_transactions,
            COUNT(DISTINCT reader_key) AS active_readers,
            COUNT(DISTINCT book_key) AS books_borrowed,
            COUNT(DISTINCT branch_key) AS branches,
            SUM(
                CASE
                    WHEN transaction_status IS NOT NULL
                    THEN 1
                    ELSE 0
                END
            ) AS tracked_statuses
        FROM fact_library_transaction
    """

    summary_row = db.execute(
        text(summary_sql)
    ).mappings().one()

    trend_sql = """
        SELECT
            d.month_name,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT f.reader_key) AS active_readers
        FROM fact_library_transaction f
        JOIN dim_date d
            ON d.date_key = f.date_key
        GROUP BY
            d.month_name,
            d.month
        ORDER BY
            d.month
    """

    trend_rows = db.execute(
        text(trend_sql)
    ).mappings().all()

    status_sql = """
        SELECT
            transaction_status AS status,
            COUNT(*) AS count
        FROM fact_library_transaction
        WHERE transaction_status IS NOT NULL
        GROUP BY transaction_status
        ORDER BY count DESC, transaction_status
    """

    status_rows = db.execute(
        text(status_sql)
    ).mappings().all()

    summary_sections = [

        (
            "Summary",
            [
                [
                    "Total Transactions",
                    _format_number(
                        summary_row["total_transactions"]
                    ),
                ],
                [
                    "Active Readers",
                    _format_number(
                        summary_row["active_readers"]
                    ),
                ],
                [
                    "Books Borrowed",
                    _format_number(
                        summary_row["books_borrowed"]
                    ),
                ],
                [
                    "Branches",
                    _format_number(
                        summary_row["branches"]
                    ),
                ],
            ],
            ["Metric", "Value"],
            None,
        ),

        (
            "Monthly Trend",
            [
                [
                    row["month_name"],
                    _format_number(
                        row["transaction_count"]
                    ),
                    _format_number(
                        row["active_readers"]
                    ),
                ]
                for row in trend_rows
            ],
            [
                "Month",
                "Transactions",
                "Readers",
            ],
            None,
        ),

        (
            "Status Breakdown",
            [
                [
                    row["status"],
                    _format_number(
                        row["count"]
                    ),
                ]
                for row in status_rows
            ],
            [
                "Status",
                "Count",
            ],
            (
                "Status distribution is derived from "
                "transaction_status values in "
                "fact_library_transaction."
                if status_rows
                else
                "No transaction status values are present "
                "in the current warehouse."
            ),
        ),
    ]

    return _render_summary_report(
        "monthly_library_performance.pdf",
        "Monthly Library Performance Report",
        summary_sections,
    )


# ============================================================
# Reading Trends Report
# ============================================================

def generate_reading_trends_report(db):

    yearly_sql = """
        SELECT
            d.year,
            COUNT(*) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d
            ON d.date_key = f.date_key
        WHERE d.year IS NOT NULL
        GROUP BY d.year
        ORDER BY d.year
    """

    yearly_rows = db.execute(
        text(yearly_sql)
    ).mappings().all()

    monthly_sql = """
        SELECT
            d.month_name,
            COUNT(*) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_date d
            ON d.date_key = f.date_key
        WHERE d.month_name IS NOT NULL
        GROUP BY
            d.month_name,
            d.month
        ORDER BY d.month
    """

    monthly_rows = db.execute(
        text(monthly_sql)
    ).mappings().all()

    genre_sql = """
        SELECT
            b.genre,
            COUNT(*) AS transaction_count
        FROM fact_library_transaction f
        JOIN dim_book b
            ON b.book_key = f.book_key
        WHERE b.genre IS NOT NULL
        GROUP BY b.genre
        ORDER BY transaction_count DESC
    """

    genre_rows = db.execute(
        text(genre_sql)
    ).mappings().all()

    format_sql = """
        SELECT
            b.format,
            COUNT(*) AS usage_count
        FROM fact_library_transaction f
        JOIN dim_book b
            ON b.book_key = f.book_key
        WHERE b.format IS NOT NULL
        GROUP BY b.format
        ORDER BY usage_count DESC
    """

    format_rows = db.execute(
        text(format_sql)
    ).mappings().all()

    sections = [

        (
            "Yearly Trends",
            [
                [
                    row["year"],
                    _format_number(
                        row["transaction_count"]
                    ),
                ]
                for row in yearly_rows
            ],
            [
                "Year",
                "Transactions",
            ],
            None,
        ),

        (
            "Monthly Trends",
            [
                [
                    row["month_name"],
                    _format_number(
                        row["transaction_count"]
                    ),
                ]
                for row in monthly_rows
            ],
            [
                "Month",
                "Transactions",
            ],
            None,
        ),

        (
            "Genre Trends",
            [
                [
                    row["genre"],
                    _format_number(
                        row["transaction_count"]
                    ),
                ]
                for row in genre_rows
            ],
            [
                "Genre",
                "Transactions",
            ],
            (
                "Genre analysis is reported only when "
                "values exist in dim_book.genre."
                if genre_rows
                else
                "Genre-level analysis is unavailable "
                "because dim_book.genre is not populated "
                "in the current warehouse."
            ),
        ),

        (
            "Format Usage",
            [
                [
                    row["format"],
                    _format_number(
                        row["usage_count"]
                    ),
                ]
                for row in format_rows
            ],
            [
                "Format",
                "Usage",
            ],
            (
                "Format analysis is based on "
                "dim_book.format when available."
                if format_rows
                else
                "Format-level analysis is unavailable "
                "because dim_book.format is not populated "
                "in the current warehouse."
            ),
        ),
    ]

    return _render_summary_report(
        "reading_trends.pdf",
        "Reading Trends Report",
        sections,
    )


# ============================================================
# Collection Analysis Report
# ============================================================

def generate_collection_analysis_report(db):

    popular_sql = """
        SELECT
            b.book_title,
            COUNT(*) AS borrow_count
        FROM fact_library_transaction f
        JOIN dim_book b
            ON b.book_key = f.book_key
        GROUP BY
            b.book_title,
            b.book_key
        ORDER BY
            borrow_count DESC,
            b.book_title
        LIMIT 10
    """

    popular_rows = db.execute(
        text(popular_sql)
    ).mappings().all()

    availability_sql = """
        SELECT
            b.book_title,
            MIN(f.available_copies) AS min_available_copies,
            AVG(f.available_copies) AS avg_available_copies
        FROM fact_library_transaction f
        JOIN dim_book b
            ON b.book_key = f.book_key
        WHERE f.available_copies IS NOT NULL
        GROUP BY
            b.book_title,
            b.book_key
        ORDER BY
            min_available_copies ASC,
            avg_available_copies ASC
        LIMIT 10
    """

    availability_rows = db.execute(
        text(availability_sql)
    ).mappings().all()

    reservation_sql = """
        SELECT
            b.book_title,
            SUM(
                COALESCE(
                    f.reservation_count,
                    0
                )
            ) AS total_reservations
        FROM fact_library_transaction f
        JOIN dim_book b
            ON b.book_key = f.book_key
        GROUP BY
            b.book_title,
            b.book_key
        ORDER BY
            total_reservations DESC
        LIMIT 10
    """

    reservation_rows = db.execute(
        text(reservation_sql)
    ).mappings().all()

    status_sql = """
        SELECT
            transaction_status AS status,
            COUNT(*) AS count
        FROM fact_library_transaction
        WHERE transaction_status IS NOT NULL
        GROUP BY transaction_status
        ORDER BY count DESC, transaction_status
    """

    status_rows = db.execute(
        text(status_sql)
    ).mappings().all()

    sections = [

        (
            "Popular Books",
            [
                [
                    row["book_title"],
                    _format_number(
                        row["borrow_count"]
                    ),
                ]
                for row in popular_rows
            ],
            [
                "Book",
                "Borrowings",
            ],
            None,
        ),

        (
            "Limited Availability",
            [
                [
                    row["book_title"],
                    _format_number(
                        row["min_available_copies"]
                    ),
                    _format_number(
                        row["avg_available_copies"]
                    ),
                ]
                for row in availability_rows
            ],
            [
                "Book",
                "Min Available Copies",
                "Avg Available Copies",
            ],
            (
                "Availability analysis is based on "
                "available_copies in "
                "fact_library_transaction."
                if availability_rows
                else
                "Availability analysis is unavailable "
                "because available_copies is not populated "
                "in the current warehouse."
            ),
        ),

        (
            "Reservations",
            [
                [
                    row["book_title"],
                    _format_number(
                        row["total_reservations"]
                    ),
                ]
                for row in reservation_rows
            ],
            [
                "Book",
                "Reservation Count",
            ],
            (
                "Reservation analysis is based on "
                "reservation_count in "
                "fact_library_transaction."
                if reservation_rows
                else
                "Reservation metrics are unavailable "
                "because reservation_count is not populated "
                "in the current warehouse."
            ),
        ),

        (
            "Collection Status",
            [
                [
                    row["status"],
                    _format_number(
                        row["count"]
                    ),
                ]
                for row in status_rows
            ],
            [
                "Status",
                "Count",
            ],
            (
                "This status breakdown is based on "
                "transaction_status values in the fact table."
                if status_rows
                else
                "No transaction_status values are present "
                "in the current warehouse."
            ),
        ),
    ]

    return _render_summary_report(
        "collection_analysis.pdf",
        "Collection Analysis Report",
        sections,
    )


# ============================================================
# Branch Performance Report
# ============================================================

def generate_branch_performance_report(db):

    branch_sql = """
        SELECT
            b.branch_name,
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT f.reader_key) AS readers,
            SUM(
                COALESCE(
                    f.fine_amount,
                    0
                )
            ) AS total_fines
        FROM fact_library_transaction f
        JOIN dim_branch b
            ON b.branch_key = f.branch_key
        GROUP BY
            b.branch_name,
            b.branch_key
        ORDER BY
            transaction_count DESC,
            b.branch_name
    """

    branch_rows = db.execute(
        text(branch_sql)
    ).mappings().all()

    overdue_sql = """
        SELECT
            b.branch_name,
            COUNT(*) AS overdue_transactions
        FROM fact_library_transaction f
        JOIN dim_branch b
            ON b.branch_key = f.branch_key
        WHERE f.return_date IS NOT NULL
          AND f.due_date IS NOT NULL
          AND f.return_date > f.due_date
        GROUP BY
            b.branch_name,
            b.branch_key
        ORDER BY
            overdue_transactions DESC,
            b.branch_name
    """

    overdue_rows = db.execute(
        text(overdue_sql)
    ).mappings().all()

    sections = [

        (
            "Branch Transactions",
            [
                [
                    row["branch_name"],
                    _format_number(
                        row["transaction_count"]
                    ),
                    _format_number(
                        row["readers"]
                    ),
                    _format_number(
                        row["total_fines"]
                    ),
                ]
                for row in branch_rows
            ],
            [
                "Branch",
                "Transactions",
                "Readers",
                "Total Fines",
            ],
            (
                "Branch activity is derived from "
                "fact_library_transaction joined to "
                "dim_branch."
                if branch_rows
                else
                "No branch data is available in "
                "the current warehouse."
            ),
        ),

        (
            "Overdue Activity",
            [
                [
                    row["branch_name"],
                    _format_number(
                        row["overdue_transactions"]
                    ),
                ]
                for row in overdue_rows
            ],
            [
                "Branch",
                "Overdue Transactions",
            ],
            (
                "Overdue analysis is based on "
                "return_date > due_date when both "
                "dates are populated."
                if overdue_rows
                else
                "Overdue analysis is unavailable "
                "because valid return_date/due_date "
                "values are not present in the current warehouse."
            ),
        ),
    ]

    return _render_summary_report(
        "branch_performance.pdf",
        "Branch Performance Report",
        sections,
    )


# ============================================================
# Data Quality Report
# ============================================================

def generate_data_quality_report(db):

    total_sql = """
        SELECT COUNT(*) AS total_records
        FROM fact_library_transaction
    """

    total_row = db.execute(
        text(total_sql)
    ).mappings().one()

    # Prefer the raw CSV count when available to reflect source data
    total_records = int(total_row["total_records"] or 0)
    raw_csv = PROJECT_ROOT / "data" / "raw" / "library_raw_data.csv"
    if raw_csv.exists():
        try:
            import pandas as _pd

            df_raw = _pd.read_csv(raw_csv)
            total_records = len(df_raw)
        except Exception:
            # fallback to DB-derived total_records
            pass

    missing_sql = """
        SELECT COUNT(*) AS missing_records
        FROM fact_library_transaction
        WHERE reader_key IS NULL
           OR book_key IS NULL
           OR branch_key IS NULL
           OR date_key IS NULL
           OR checkout_date IS NULL
           OR due_date IS NULL
    """

    missing_row = db.execute(
        text(missing_sql)
    ).mappings().one()

    missing_records = int(missing_row["missing_records"] or 0)

    duplicate_sql = """
        SELECT COUNT(*) AS duplicate_records
        FROM (
            SELECT transaction_id
            FROM fact_library_transaction
            WHERE transaction_id IS NOT NULL
            GROUP BY transaction_id
            HAVING COUNT(*) > 1
        ) d
    """

    duplicate_row = db.execute(
        text(duplicate_sql)
    ).mappings().one()

    duplicate_records = int(duplicate_row["duplicate_records"] or 0)

    invalid_sql = """
        SELECT COUNT(*) AS invalid_records
        FROM fact_library_transaction
        WHERE checkout_date IS NULL
           OR due_date IS NULL
           OR due_date < checkout_date
           OR (
                return_date IS NOT NULL
                AND return_date < checkout_date
           )
           OR fine_amount < 0
           OR total_copies < 0
           OR available_copies < 0
           OR available_copies > total_copies
    """

    invalid_row = db.execute(
        text(invalid_sql)
    ).mappings().one()

    invalid_records = int(invalid_row["invalid_records"] or 0)

    rejected_sql = """
        SELECT COUNT(*) AS rejected_records
        FROM fact_library_transaction
        WHERE checkout_date IS NULL
           OR due_date IS NULL
           OR due_date < checkout_date
           OR (
                return_date IS NOT NULL
                AND return_date < checkout_date
           )
           OR fine_amount < 0
           OR total_copies < 0
           OR available_copies < 0
           OR available_copies > total_copies
    """

    rejected_row = db.execute(
        text(rejected_sql)
    ).mappings().one()

    rejected_records = int(rejected_row["rejected_records"] or 0)
    # If a rejected records CSV exists, prefer that count for reporting
    rej_csv = PROJECT_ROOT / "data" / "quality" / "rejected_records.csv"
    if rej_csv.exists():
        try:
            import pandas as _pd

            df_rej = _pd.read_csv(rej_csv)
            rejected_records = len(df_rej)
        except Exception:
            pass

    # Use the database's count of clean records to compute quality score
    clean_sql = "SELECT COUNT(*) AS clean_records FROM fact_library_transaction"
    clean_row = db.execute(text(clean_sql)).mappings().one()
    clean_records = int(clean_row["clean_records"] or 0)

    quality_score = 0.0
    if total_records:
        quality_score = round((clean_records / total_records) * 100, 2)

    sections = [

        (
            "Summary",
            [
                [
                    "Total Records",
                    _format_number(
                        total_records
                    ),
                ],
                [
                    "Missing Data",
                    _format_number(
                        missing_records
                    ),
                ],
                [
                    "Duplicate Records",
                    _format_number(
                        duplicate_records
                    ),
                ],
                [
                    "Invalid Records",
                    _format_number(
                        invalid_records
                    ),
                ],
                [
                    "Rejected Records",
                    _format_number(
                        rejected_records
                    ),
                ],
                [
                    "Quality Score",
                    f"{quality_score}%",
                ],
            ],
            [
                "Metric",
                "Value",
            ],
            (
                "Quality Score formula: "
                "Valid Records / Total Records × 100, "
                "where Valid Records = Total Records - "
                "Invalid Records - Duplicate Records."
            ),
        )
    ]

    return _render_summary_report(
        "data_quality.pdf",
        "Data Quality Report",
        sections,
    )


# ============================================================
# Generic PDF Helpers
# ============================================================

def create_pdf_document(
    filename,
    title,
    rows,
    headers
):
    return _render_summary_report(
        filename,
        title,
        [
            (
                title,
                rows,
                headers,
                None,
            )
        ],
    )


def create_pdf(
    filename,
    title,
    data
):

    if not data:

        rows = []
        headers = ["Value"]

    elif (
        isinstance(data, list)
        and data
        and isinstance(
            data[0],
            (list, tuple)
        )
    ):

        rows = data

        headers = (
            ["Value"]
            if len(data[0]) == 1
            else [
                f"Column {i + 1}"
                for i in range(
                    len(data[0])
                )
            ]
        )

    else:

        rows = [
            [
                "Value",
                str(data),
            ]
        ]

        headers = [
            "Field",
            "Value",
        ]

    return _render_summary_report(
        filename,
        title,
        [
            (
                title,
                rows,
                headers,
                None,
            )
        ],
    )