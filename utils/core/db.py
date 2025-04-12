import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Generator, List
import os

from utils.common.constants import DB_FILE

from .paths import get_file_path


@contextmanager
def get_db(profile=None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for accessing the SQLite database.

    Yields:
        sqlite3.Connection: Database connection object.
    """
    db_path = get_file_path(DB_FILE, profile)
    
    # Ensure the database directory exists
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # Ensure tables are created and schema is updated
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT,
                    tags TEXT,
                    length INTEGER NOT NULL,
                    rating REAL NOT NULL DEFAULT 0,
                    member TEXT NOT NULL,
                    score REAL NOT NULL DEFAULT 0,
                    date_added TEXT NOT NULL,
                    read_date TEXT
                )
                """
            )
            # Add columns if they don't exist
            cursor = conn.execute("PRAGMA table_info(books)")
            columns = [col[1] for col in cursor.fetchall()]
            if "isbn" not in columns:
                conn.execute("ALTER TABLE books ADD COLUMN isbn TEXT")
            if "tags" not in columns:
                conn.execute("ALTER TABLE books ADD COLUMN tags TEXT")

        yield conn
    finally:
        conn.close()


def read_db(db_file_or_profile=None, profile=None) -> List[Dict[str, Any]]:
    """
    Reads all books from the database.
    
    Args:
        db_file_or_profile: Can be either a database file path or a profile name
        profile: Profile name (used only if first argument is a db_file)
    
    Returns:
        List[Dict[str, Any]]: A list of books as dictionaries.
    """
    # If first argument is None or looks like a profile name, treat it as profile
    if db_file_or_profile is None or isinstance(db_file_or_profile, str):
        actual_profile = db_file_or_profile
    else:
        actual_profile = profile
        
    with get_db(actual_profile) as conn:
        cursor = conn.execute("SELECT * FROM books")
        return [dict(row) for row in cursor.fetchall()]


def write_db(data: List[Dict[str, Any]], profile=None):
    """
    Writes a list of books to the database.

    Args:
        data (List[Dict[str, Any]]): List of book dictionaries to insert.
    """
    with get_db(profile) as conn:
        try:
            update_books_table(conn, data)
        except Exception as e:
            conn.execute("ROLLBACK")
            print(f"Error updating database: {e}")
            raise


def update_books_table(conn, data):
    conn.execute("BEGIN TRANSACTION")
    # Create a temporary table to validate data before replacing
    conn.execute(
        """
                CREATE TEMPORARY TABLE books_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT,
                    tags TEXT,
                    length INTEGER NOT NULL,
                    rating REAL NOT NULL DEFAULT 0,
                    member TEXT NOT NULL,
                    score REAL NOT NULL DEFAULT 0,
                    date_added TEXT NOT NULL,
                    read_date TEXT
                )
                """
    )
    # Ensure every book has an ISBN and tags
    for book in data:
        if "isbn" not in book or not book["isbn"]:
            book["isbn"] = "N/A"  # Assign default value if missing
        if "tags" not in book or not book["tags"]:
            book["tags"] = ""  # Assign empty string if missing

    # Insert data into temporary table
    conn.executemany(
        """
                INSERT INTO books_temp (
                    title, author, isbn, tags, length, rating, member, 
                    score, date_added, read_date
                ) VALUES (
                    :title, :author, :isbn, :tags, :length, :rating, :member,
                    :score, :date_added, :read_date
                )
                """,
        data,
    )

    # Replace the main table with data from the temporary table
    conn.execute("DELETE FROM books")
    conn.execute(
        """
                INSERT INTO books 
                SELECT * FROM books_temp
                """
    )

    conn.execute("COMMIT")
    conn.execute("DROP TABLE books_temp")

    print(f"Database updated with {len(data)} books.")