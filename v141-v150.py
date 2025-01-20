import os
import sqlite3
from pathlib import Path

# Define the root directory for profiles
root_dir = os.path.expandvars(r"%appdata%/FabulaRasa/profiles")

# Define the desired column order including the new 'tags' column
desired_columns = [
    "id", "title", "author", "isbn", "tags", "length", "rating", "member", "score", "date_added", "read_date"
]

# Function to process each books.db file
def process_db(db_path):
    print(f"Processing: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current column structure
    cursor.execute("PRAGMA table_info(books)")
    current_columns = [info[1] for info in cursor.fetchall()]

    # Check if 'tags' column exists and is in the correct position
    if current_columns == desired_columns:
        print("Table already has the correct structure.")
        conn.close()
        return

    # Create a new table with the desired structure
    new_columns_def = ", ".join(
        f"{col} TEXT" if col != "id" else "id INTEGER PRIMARY KEY"
        for col in desired_columns
    )
    cursor.execute(f"CREATE TABLE books_new ({new_columns_def})")

    # Map current data to the new table structure
    insert_columns = ", ".join(desired_columns)
    select_columns = ", ".join(
        col if col in current_columns else "'' AS " + col for col in desired_columns
    )
    cursor.execute(f"INSERT INTO books_new ({insert_columns}) SELECT {select_columns} FROM books")

    # Replace the old table with the new table
    cursor.execute("DROP TABLE books")
    cursor.execute("ALTER TABLE books_new RENAME TO books")

    conn.commit()
    conn.close()
    print("Updated successfully.")

# Traverse the profiles directory and update each books.db
for profile_dir in Path(root_dir).rglob("books.db"):
    process_db(str(profile_dir))
