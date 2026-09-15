"""
API tests for LibraSight FastAPI backend.

These tests verify that the main API endpoints are available
and return successful responses.

The tests use the existing PostgreSQL-backed FastAPI application.
They do not modify the database.
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# IMPORT FASTAPI APPLICATION
# ============================================================

from app.main import app


# ============================================================
# TEST CLIENT
# ============================================================

client = TestClient(app)


# ============================================================
# HELPER
# ============================================================

def check_get_endpoint(endpoint):
    """
    Send a GET request and verify that the endpoint responds.

    A successful API endpoint should normally return HTTP 200.
    """

    response = client.get(endpoint)

    assert response.status_code == 200, (
        f"GET {endpoint} failed.\n"
        f"Status code: {response.status_code}\n"
        f"Response: {response.text}"
    )

    return response


# ============================================================
# ROOT ENDPOINT
# ============================================================

def test_root_endpoint():
    """
    Verify the root API endpoint.
    """

    response = check_get_endpoint("/")

    data = response.json()

    assert isinstance(data, dict)

    assert data.get("message") == (
        "LibraSight API is running"
    )


# ============================================================
# HEALTH ENDPOINT
# ============================================================

def test_health_endpoint():
    """
    Verify the health-check endpoint.
    """

    response = check_get_endpoint("/health")

    data = response.json()

    assert isinstance(data, dict)

    assert data.get("status") == "healthy"


# ============================================================
# DASHBOARD
# ============================================================

def test_dashboard_summary():
    """
    Verify dashboard summary endpoint.
    """

    response = check_get_endpoint(
        "/dashboard/summary"
    )

    data = response.json()

    assert isinstance(data, dict)


def test_dashboard_trends():
    """
    Verify dashboard trends endpoint.
    """

    response = check_get_endpoint(
        "/dashboard/trends"
    )

    data = response.json()

    assert data is not None


def test_dashboard_status():
    """
    Verify dashboard transaction-status endpoint.
    """

    response = check_get_endpoint(
        "/dashboard/status"
    )

    data = response.json()

    assert data is not None


# ============================================================
# BOOKS
# ============================================================

def test_books_endpoint():
    """
    Verify the books endpoint.
    """

    response = check_get_endpoint(
        "/books"
    )

    data = response.json()

    assert data is not None


def test_top_books_endpoint():
    """
    Verify the top-books analytics endpoint.
    """

    response = check_get_endpoint(
        "/books/top"
    )

    data = response.json()

    assert data is not None


def test_book_genres_endpoint():
    """
    Verify the book-genre analytics endpoint.
    """

    response = check_get_endpoint(
        "/books/genres"
    )

    data = response.json()

    assert data is not None


# ============================================================
# READERS
# ============================================================

def test_readers_endpoint():
    """
    Verify the readers endpoint.
    """

    response = check_get_endpoint(
        "/readers"
    )

    data = response.json()

    assert data is not None


def test_reader_types_endpoint():
    """
    Verify reader-type analytics endpoint.
    """

    response = check_get_endpoint(
        "/readers/types"
    )

    data = response.json()

    assert data is not None


def test_reader_activity_endpoint():
    """
    Verify reader-activity analytics endpoint.
    """

    response = check_get_endpoint(
        "/readers/activity"
    )

    data = response.json()

    assert data is not None


# ============================================================
# BRANCHES
# ============================================================

def test_branches_endpoint():
    """
    Verify the branches endpoint.
    """

    response = check_get_endpoint(
        "/branches"
    )

    data = response.json()

    assert data is not None


def test_branch_performance_endpoint():
    """
    Verify branch-performance analytics endpoint.
    """

    response = check_get_endpoint(
        "/branches/performance"
    )

    data = response.json()

    assert data is not None


# ============================================================
# COLLECTION
# ============================================================

def test_collection_endpoints_are_registered():
    """
    Verify that the collection endpoint is registered.
    """

    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/collection/summary" in routes, (
        "Collection summary endpoint is not registered."
    )


def test_data_quality_endpoints_are_registered():
    """
    Verify that the data quality endpoints are registered.
    """

    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/data-quality/summary" in routes, (
        "Data quality summary endpoint is not registered."
    )

    assert "/data-quality/rejected" in routes, (
        "Rejected records endpoint is not registered."
    )


def test_reports_router_is_registered():
    """
    Verify that the main report endpoints are registered.
    """

    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    expected_routes = {
        "/reports/monthly-performance",
        "/reports/monthly",
        "/reports/reading-trends",
        "/reports/collection-analysis",
        "/reports/collection",
        "/reports/branch-performance",
        "/reports/branch",
        "/reports/data-quality",
    }

    missing_routes = expected_routes - routes

    assert not missing_routes, (
        f"Missing report endpoints: {sorted(missing_routes)}"
    )


def test_notifications_router_is_registered():
    """
    Verify that the notifications endpoint is registered.
    """

    routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    assert "/notifications/" in routes, (
        "Notifications endpoint is not registered."
    )

# ============================================================
# OPENAPI
# ============================================================

def test_openapi_documentation():
    """
    Verify that FastAPI's OpenAPI documentation is available.
    """

    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert "paths" in data

    assert len(data["paths"]) > 0