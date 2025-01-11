import sqlite3
from typing import List, Dict, Any
from .paths import get_file_path
from contextlib import contextmanager

DB_FILE = "books.db"

@contextmanager
def get_db(profile=None) -> sqlite3.Connection:
    conn = sqlite3.connect(get_file_path(DB_FILE, profile))
    conn.row_factory = sqlite3.Row
    
    try:
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
        yield conn
    finally:
        conn.close()

def read_db(filename, profile=None) -> List[Dict[str, Any]]:
    with get_db(profile) as conn:
        cursor = conn.execute("SELECT * FROM books")
        return [dict(row) for row in cursor.fetchall()]

def write_db(filename, data, headers, profile=None):
    with get_db(profile) as conn:
        # Start a transaction
        try:
            # Instead of deleting all records, we'll use a transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Create a temporary table
            conn.execute("""
                CREATE TEMPORARY TABLE books_temp (
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
            
            # Insert new data into temporary table
            conn.executemany(
                """
                INSERT INTO books_temp (
                    title, author, length, rating, member, 
                    score, date_added, read_date
                ) VALUES (
                    :title, :author, :length, :rating, :member,
                    :score, :date_added, :read_date
                )
                """,
                data
            )
            
            # Clear main table and copy temp data
            conn.execute("DELETE FROM books")
            conn.execute("""
                INSERT INTO books 
                SELECT * FROM books_temp
            """)
            
            # Commit transaction
            conn.execute("COMMIT")
            
            # Clean up temp table
            conn.execute("DROP TABLE books_temp")
            
            print(f"Database updated with {len(data)} books.")
            
        except Exception as e:
            # If anything goes wrong, roll back to preserve existing data
            conn.execute("ROLLBACK")
            print(f"Error updating database: {e}")
            raise