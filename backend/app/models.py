from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Integer,
    Numeric,
    String,
    ForeignKey,
)

from app.database import Base


# ============================================================
# DIM_DATE
# ============================================================

class DimDate(Base):

    __tablename__ = "dim_date"

    date_key = Column(
        Integer,
        primary_key=True
    )

    full_date = Column(
        Date,
        nullable=False
    )

    day = Column(Integer)

    month = Column(Integer)

    month_name = Column(String)

    quarter = Column(Integer)

    year = Column(Integer)


# ============================================================
# DIM_READER
# ============================================================

class DimReader(Base):

    __tablename__ = "dim_reader"

    reader_key = Column(
        Integer,
        primary_key=True
    )

    reader_id = Column(String)

    reader_name = Column(String)

    age = Column(Integer)

    gender = Column(String)

    reader_type = Column(String)

    membership_date = Column(Date)

    home_branch_id = Column(String)


# ============================================================
# DIM_BOOK
# ============================================================

class DimBook(Base):

    __tablename__ = "dim_book"

    book_key = Column(
        Integer,
        primary_key=True
    )

    book_id = Column(String)

    isbn = Column(String)

    book_title = Column(String)

    author = Column(String)

    genre = Column(String)

    publication_year = Column(Integer)

    language = Column(String)

    format = Column(String)

    publisher = Column(String)


# ============================================================
# DIM_BRANCH
# ============================================================

class DimBranch(Base):

    __tablename__ = "dim_branch"

    branch_key = Column(
        Integer,
        primary_key=True
    )

    branch_id = Column(String)

    branch_name = Column(String)

    city = Column(String)

    area = Column(String)

    library_type = Column(String)

    branch_capacity = Column(Integer)


# ============================================================
# FACT_LIBRARY_TRANSACTION
# ============================================================

class FactLibraryTransaction(Base):

    __tablename__ = "fact_library_transaction"

    transaction_key = Column(
        Integer,
        primary_key=True
    )

    transaction_id = Column(String)

    reader_key = Column(
        Integer,
        ForeignKey("dim_reader.reader_key")
    )

    book_key = Column(
        Integer,
        ForeignKey("dim_book.book_key")
    )

    branch_key = Column(
        Integer,
        ForeignKey("dim_branch.branch_key")
    )

    date_key = Column(
        Integer,
        ForeignKey("dim_date.date_key")
    )

    checkout_date = Column(Date)

    due_date = Column(Date)

    return_date = Column(Date)

    transaction_status = Column(String)

    renewal_count = Column(Integer)

    reservation_flag = Column(Boolean)

    reservation_count = Column(Integer)

    checkout_method = Column(String)

    fine_amount = Column(Numeric)

    total_copies = Column(Integer)

    available_copies = Column(Integer)