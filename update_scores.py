from utils.db import read_csv_file, write_csv_file
from utils.selection import calculate_scores

# Read existing data
books = read_csv_file("books.csv")

# Convert ratings to float
for book in books:
    book["rating"] = float(book["rating"])

# Recalculate scores
books = calculate_scores(books)

# Save back to CSV
headers = ["title", "author", "length", "rating", "member", "score", 
          "date_added", "date_selected"]
write_csv_file("books.csv", books, headers)