import contextlib
import sqlite3
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from utils.common.constants import DB_FILE


def get_script_dir():
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def get_data_dir(profile=None) -> str:
    app_data = os.getenv("APPDATA")
    if not app_data:
        print("Error: APPDATA environment variable not found")
        sys.exit(1)

    base_path = Path(app_data) / "FabulaRasa" / "profiles"

    # Always use 'default' profile if none specified
    profile = profile or "default"
    base_path = base_path / profile

    base_path.mkdir(parents=True, exist_ok=True)
    return str(base_path)


def get_profiles() -> list:
    app_data = os.getenv("APPDATA")
    if not app_data:
        print("Error: APPDATA environment variable not found")
        sys.exit(1)

    base_dir = Path(app_data) / "FabulaRasa" / "profiles"

    profiles = []
    with contextlib.suppress(FileNotFoundError):
        profiles.extend(
            item
            for item in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, item))
        )
    return profiles or ["default"]


def backup_database(db_path, profile):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(get_data_dir(profile)) / "backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / DB_FILE
    shutil.copy2(db_path, backup_path)
    print(f"Backup created at: {backup_path}")


def migrate_database(db_path, profile):
    if not os.path.exists(db_path):
        print(f"Skipping: Database not found at {db_path}")
        return False

    print(f"\nMigrating database: {db_path}")

    backup_database(db_path, profile)

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        return add_isbn_column(conn, cursor)
    except Exception as e:
        conn.execute("ROLLBACK")
        print(f"Error during migration: {e}")
        return False
    finally:
        conn.close()


def add_isbn_column(conn, cursor):
    # Start transaction
    conn.execute("BEGIN TRANSACTION")

    # Create temporary table with new schema
    cursor.execute(
        """ 
            CREATE TEMPORARY TABLE books_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                length INTEGER NOT NULL,
                rating REAL NOT NULL DEFAULT 0,
                member TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                date_added TEXT NOT NULL,
                read_date TEXT
            )
        """
    )

    # Copy data from old table to temp table, adding 'N/A' for isbn
    cursor.execute(
        """
            INSERT INTO books_temp (title, author, isbn, length, rating, member, score, date_added, read_date)
            SELECT title, author, 'N/A', length, rating, member, score, date_added, read_date
            FROM books
        """
    )

    cursor.execute("DROP TABLE books")

    # Create new table
    cursor.execute(
        """
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                length INTEGER NOT NULL,
                rating REAL NOT NULL DEFAULT 0,
                member TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                date_added TEXT NOT NULL,
                read_date TEXT
            )
        """
    )

    # Copy data from temp table to new table
    cursor.execute(
        """
            INSERT INTO books 
            SELECT * FROM books_temp
        """
    )

    conn.execute("COMMIT")
    print("Database migration completed successfully!")
    return True


def migrate_all_profiles():
    # Change to script directory first
    os.chdir(get_script_dir())

    profiles = get_profiles()
    print(f"Found profiles: {', '.join(profiles)}")

    success_count = 0
    for profile in profiles:
        db_path = os.path.join(get_data_dir(profile), DB_FILE)
        if migrate_database(db_path, profile):
            success_count += 1

    print(
        f"\nMigration complete! Successfully migrated {success_count} of {len(profiles)} databases."
    )


if __name__ == "__main__":
    migrate_all_profiles()
