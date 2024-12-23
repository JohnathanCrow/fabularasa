"""Database operations module."""
import csv
from .paths import get_file_path

def read_csv_file(filename):
    """Read data from a CSV file and return as a list of dictionaries."""
    books = []
    filepath = get_file_path(filename)
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                books.append(row)
    except FileNotFoundError:
        print(f"{filepath} not found.")
    return books

def write_csv_file(filename, data, headers):
    """Write data to a CSV file."""
    filepath = get_file_path(filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"CSV updated with {len(data)} books.")