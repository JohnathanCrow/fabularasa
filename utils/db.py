"""Database operations module."""
import sqlite3
from typing import List, Dict, Any
from .paths import get_file_path

DB_FILE = "books.db"

def get_db() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(get_file_path(DB_FILE))
    conn.row_factory = sqlite3.Row
    
    # Create table if it doesn't exist
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                length INTEGER NOT NULL,
                rating REAL NOT NULL DEFAULT 0,
                member TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                date_added TEXT NOT NULL,
                read_date TEXT
            )
        """)
    return conn

def read_csv_file(filename) -> List[Dict[str, Any]]:
    """Read all books from database."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT * FROM books"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def write_csv_file(filename, data, headers):
    """Write books to database."""
    conn = get_db()
    try:
        with conn:
            # Clear existing data
            conn.execute("DELETE FROM books")
            
            # Insert new data
            conn.executemany(
                """
                INSERT INTO books (
                    title, author, length, rating, member, 
                    score, date_added, read_date
                ) VALUES (
                    :title, :author, :length, :rating, :member,
                    :score, :date_added, :read_date
                )
                """,
                data
            )
    finally:
        conn.close()
    print(f"Database updated with {len(data)} books.")