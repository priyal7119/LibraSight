import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# PostgreSQL configuration
# ============================================================

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")


# ============================================================
# LOCAL WINDOWS / DOCKER HOST HANDLING
# ============================================================

# host.docker.internal is required when the application
# runs inside Docker and PostgreSQL runs on the Windows host.
#
# When running directly on Windows, localhost should be used.

if os.name == "nt" and DATABASE_HOST == "host.docker.internal":
    DATABASE_HOST = "localhost"


# ============================================================
# Validate configuration
# ============================================================

required_variables = {
    "DATABASE_HOST": DATABASE_HOST,
    "DATABASE_PORT": DATABASE_PORT,
    "DATABASE_NAME": DATABASE_NAME,
    "DATABASE_USER": DATABASE_USER,
    "DATABASE_PASSWORD": DATABASE_PASSWORD,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    raise RuntimeError(
        "Missing database environment variables: "
        + ", ".join(missing_variables)
    )


# ============================================================
# PostgreSQL connection URL
# ============================================================

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/"
    f"{DATABASE_NAME}"
)


# ============================================================
# SQLAlchemy Engine
# ============================================================

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )
except Exception as e:
    # Fallback to SQLite for development/testing when psycopg2 is unavailable
    # This avoids import errors for the PostgreSQL driver.
    # The fallback uses an in‑memory SQLite database.
    import warnings
    warnings.warn(
        f"Failed to create PostgreSQL engine ({e}). Falling back to SQLite in‑memory database.",
        RuntimeWarning,
    )
    engine = create_engine("sqlite:///:memory:", echo=False)


# ============================================================
# Database Session
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# Base class for SQLAlchemy models
# ============================================================

Base = declarative_base()


# ============================================================
# Database Dependency
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()