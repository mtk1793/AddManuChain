from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url # ADDED
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables first to ensure DATABASE_URL from .env is available if set
load_dotenv()

# Define the base directory for the application
# In Docker, this will be /app.
DOCKER_APP_DIR = "/app"
DATA_DIR_NAME = "data"

# Determine if running in Docker by checking for a common Docker env var or path
# This is a heuristic. A more robust way might be an explicit env var like RUNNING_IN_DOCKER=true
IS_DOCKER = os.path.exists(DOCKER_APP_DIR) and os.getcwd().startswith(DOCKER_APP_DIR)

# Define database paths
DEFAULT_SQLITE_DB_NAME = "mitacs_dashboard.db"

if IS_DOCKER:
    PROJECT_ROOT = DOCKER_APP_DIR
    DATA_DIR = os.path.join(PROJECT_ROOT, DATA_DIR_NAME)
    # Force absolute path for SQLite in Docker
    DEFAULT_SQLITE_DB_PATH = os.path.join(DATA_DIR, DEFAULT_SQLITE_DB_NAME)
    DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_DB_PATH}"
else:
    # For local development, it\'s the project root relative to this file
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR = os.path.join(PROJECT_ROOT, DATA_DIR_NAME)
    DEFAULT_SQLITE_DB_PATH = os.path.abspath(os.path.join(DATA_DIR, DEFAULT_SQLITE_DB_NAME))
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_SQLITE_DB_PATH}" # Ensure three slashes for absolute path
    )

print(f"[DB Connection] IS_DOCKER: {IS_DOCKER}")
print(f"[DB Connection] Project Root: {PROJECT_ROOT}")
print(f"[DB Connection] Data Directory: {DATA_DIR}")
print(f"[DB Connection] DEFAULT_SQLITE_DB_PATH: {DEFAULT_SQLITE_DB_PATH}")
print(f"[DB Connection] Using database URL: {DATABASE_URL}")

# Ensure the data directory exists *before* creating the engine if it's SQLite
if DATABASE_URL and DATABASE_URL.startswith("sqlite:"):
    try:
        url_obj = make_url(DATABASE_URL)
        db_file_path = url_obj.database # This is the path part, e.g., /app/data/mitacs_dashboard.db

        if db_file_path and db_file_path != ":memory:":
            # DATA_DIR is the directory we expect to contain the SQLite file.
            # It's already an absolute path like /app/data or /path/to/project/data.
            if not os.path.exists(DATA_DIR):
                try:
                    os.makedirs(DATA_DIR, exist_ok=True)
                    print(f"[DB Connection] Created data directory for SQLite: {DATA_DIR}")
                except Exception as e:
                    print(f"[DB Connection] Error creating data directory {DATA_DIR}: {e}")
            # else: # Optional debug line
            #     print(f"[DB Connection] Data directory {DATA_DIR} already exists.")
        
    except Exception as e: # Catch errors from make_url or subsequent path operations
        print(f"[DB Connection] Error processing SQLite path or creating directory: {e}")
        # Depending on the error, engine creation might fail.

# Create engine and session
# Add connect_args for SQLite to handle potential threading issues with Streamlit
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Create base class for models - THIS IS THE SHARED BASE
Base = declarative_base()


@contextmanager
def get_db_session():
    """Get a database session that supports context management."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        print(f"[DB Session] Error during session: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize the database by creating all tables defined in Base.metadata."""
    # Import all models that define tables using this Base
    # Assuming models/__init__.py correctly exports all necessary model classes
    from src.db import models # This will trigger models/__init__.py

    print("[DB Init] Attempting to create all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[DB Init] ✅ Tables created successfully or already exist.")
    except Exception as e:
        print(f"[DB Init] ❌ Error creating tables: {e}")
        raise

# Example of how to call init_db if this script is run directly (for testing connection.py)
# if __name__ == "__main__":
#     print("[DB Connection Test] Initializing database directly from connection.py...")
#     init_db()
#     print("[DB Connection Test] Database initialization complete.")
#
#     # Test session
#     print("[DB Connection Test] Testing database session...")
#     try:
#         with get_db_session() as db:
#             # Example: query users if User model is simple enough or add a dummy query
#             # count = db.query(user.User).count()
#             # print(f"[DB Connection Test] Found {count} users.")
#             print("[DB Connection Test] ✅ Database session test successful.")
#     except Exception as e:
#         print(f"[DB Connection Test] ❌ Database session test failed: {e}")


