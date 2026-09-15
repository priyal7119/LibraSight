from typing import Optional

from pydantic import BaseModel


# ============================================================
# Dashboard
# ============================================================

class DashboardSummary(BaseModel):
    total_transactions: int
    total_books: int
    total_readers: int
    total_branches: int


class DashboardTrend(BaseModel):
    year: int
    month: int
    month_name: str
    transaction_count: int


class DashboardStatus(BaseModel):
    status: Optional[str]
    count: int


# ============================================================
# Books
# ============================================================

class Book(BaseModel):
    book_key: int
    book_id: Optional[str]
    isbn: Optional[str]
    book_title: Optional[str]
    author: Optional[str]
    genre: Optional[str]
    publication_year: Optional[int]
    language: Optional[str]
    format: Optional[str]
    publisher: Optional[str]


class TopBook(BaseModel):
    book_key: int
    book_title: Optional[str]
    author: Optional[str]
    genre: Optional[str]
    transaction_count: int


class GenreSummary(BaseModel):
    genre: Optional[str]
    transaction_count: int


# ============================================================
# Readers
# ============================================================

class Reader(BaseModel):
    reader_key: int
    reader_id: Optional[str]
    reader_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    reader_type: Optional[str]
    membership_date: Optional[str]
    home_branch_id: Optional[str]


class ReaderTypeSummary(BaseModel):
    reader_type: Optional[str]
    transaction_count: int


class ReaderActivity(BaseModel):
    reader_key: int
    reader_id: Optional[str]
    reader_name: Optional[str]
    reader_type: Optional[str]
    transaction_count: int
    total_fine: float


# ============================================================
# Branches
# ============================================================

class Branch(BaseModel):
    branch_key: int
    branch_id: Optional[str]
    branch_name: Optional[str]
    city: Optional[str]
    area: Optional[str]
    library_type: Optional[str]
    branch_capacity: Optional[int]


class BranchPerformance(BaseModel):
    branch_key: int
    branch_id: Optional[str]
    branch_name: Optional[str]
    city: Optional[str]
    transaction_count: int
    total_fine: float

# ============================================================
# Generic Paginated Response
# ============================================================

from typing import List, Any

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int