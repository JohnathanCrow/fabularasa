"""Module for managing book operations."""
from utils.dates import get_next_monday, format_date, get_current_date
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from utils.db import read_csv_file, write_csv_file
from utils.selection import (
    select_top_choice,
    get_selected_books,
    calculate_scores
)
from utils.scraping import GoodreadsClient

class BookManager:
    def __init__(self, parent):
        self.parent = parent
        self.book_input = None
        self.author_input = None
        self.word_count_input = None
        self.member_input = None
        self.selected_list = None
        self.cover_label = None
        self.details_label = None
        self.book_list_widget = None
        self.goodreads_client = GoodreadsClient()
        self.read_date_calendar = None

    def update_selected_list(self):
        """Update the list of selected books."""
        self.selected_list.clear()
        selected_books = get_selected_books()
        
        for book in selected_books[:20]:  # Show last 20 selections
            text = f"{book['title']}, {book['author']} ({book['member']})"
            item = QListWidgetItem(text)
            item.setFont(QFont())
            self.selected_list.addItem(item)

    def update_current_selection(self):
        """Update the current book display."""
        selected_books = get_selected_books()
        if not selected_books:
            return
            
        current_book = selected_books[0]  # Most recent book
        self._update_cover(current_book)
        self._update_details(current_book)

    def _update_cover(self, book):
        """Update the cover image display."""
        pixmap = self.goodreads_client.get_cover(book['title'])
        if pixmap:
            pixmap = pixmap.scaled(
                self.cover_label.width(), 
                self.cover_label.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio
            )
            self.cover_label.setPixmap(pixmap)
        else:
            self._set_placeholder_cover()

    def _set_placeholder_cover(self):
        """Set a placeholder cover image."""
        try:
            placeholder_path = "no_cover_available.png"
            pixmap = QPixmap(placeholder_path)
            if pixmap.isNull():
                self.cover_label.setText("No cover available")
            else:
                pixmap = pixmap.scaled(
                    self.cover_label.width(),
                    self.cover_label.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio
                )
                self.cover_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error setting placeholder: {e}")
            self.cover_label.setText("No cover available")

    def _update_details(self, book):
        """Update the details display for a book."""
        details = f"""
        <h2>{book['title']}</h2>
        <p><b>Author:</b> {book['author']}</p>
        <p><b>Words:</b> {book['length']}</p>
        <p><b>Rating:</b> {book['rating']}</p>
        <p><b>Score:</b> {book['score']}</p>
        <p><b>Member:</b> {book['member']}</p>
        <p><b>Read Date:</b> {book.get('read_date', 'Not selected')}</p>
        """
        self.details_label.setText(details)

    def parse_word_count(self, word_count_str):
        """Convert word count input like '50k' to numeric value."""
        try:
            if word_count_str.lower().endswith("k"):
                return int(float(word_count_str[:-1]) * 1000)
            return int(word_count_str)
        except ValueError:
            raise ValueError(f"Invalid word count format: {word_count_str}")

    def add_book(self):
        """Add a new book to the system."""
        try:
            query = self.book_input.text().strip()
            word_count_str = self.word_count_input.text().strip()
            member = self.member_input.text().strip()
            
            if not all([query, word_count_str]):
                self.parent.statusBar().setStyleSheet("color: red;")
                self.parent.statusBar().showMessage("Title/ISBN and wordcount are required!", 6000)
                return

            try:
                word_count = self.parse_word_count(word_count_str)
            except ValueError as e:
                self.parent.statusBar().setStyleSheet("color: red;")
                self.parent.statusBar().showMessage(str(e), 6000)
                return

            metadata = self.goodreads_client.get_book_info(query)
            if metadata:
                book_data = {
                    "title": metadata["title"],
                    "author": metadata["author"],
                    "length": word_count,
                    "rating": float(metadata["rating"]),
                    "member": member,
                    "score": 0,
                    "date_added": get_current_date(),
                    "read_date": ""
                }
            else:
                book_data = {
                    "title": query,
                    "author": self.author_input.text().strip() or "Unknown",
                    "length": word_count,
                    "rating": 0.0,
                    "member": member,
                    "score": 0,
                    "date_added": get_current_date(),
                    "read_date": ""
                }

            books = read_csv_file("books.csv")
            books.append(book_data)
            books_with_scores = calculate_scores(books)
            
            headers = ["title", "author", "length", "rating", "member", "score", 
                      "date_added", "read_date"]
            write_csv_file("books.csv", books_with_scores, headers)
            
            if self.book_list_widget:
                self.book_list_widget.load_books(books_with_scores)
            
            # Clear fields after successful addition
            self.book_input.clear()
            self.author_input.clear()
            self.word_count_input.clear()
            self.member_input.clear()
            self.book_input.setFocus()
            
            self.parent.statusBar().setStyleSheet("color: green;")
            self.parent.statusBar().showMessage("Book added successfully!", 6000)
        except Exception as e:
            print(f"Error adding book: {e}")
            self.parent.statusBar().showMessage(f"Error adding book: {str(e)}")
            
    def select_book(self):
        """Select the next book for the club."""
        books = read_csv_file("books.csv")
        books = calculate_scores(books)
        
        top_book = select_top_choice(books)
        if top_book:
            # Set the read date
            if self.read_date_calendar and self.read_date_calendar.selectedDate():
                selected_date = self.read_date_calendar.selectedDate().toPyDate()
                top_book["read_date"] = format_date(selected_date)
            else:
                selected_date = get_next_monday()
                top_book["read_date"] = format_date(selected_date)
            
            # Update the book in the CSV
            for book in books:
                if book["title"] == top_book["title"]:
                    book["read_date"] = top_book["read_date"]
            
            headers = ["title", "author", "length", "rating", "member", "score", 
                      "date_added", "read_date"]
            write_csv_file("books.csv", books, headers)
            
            self.update_selected_list()
            self.update_current_selection()
            
            if self.book_list_widget:
                self.book_list_widget.load_books(books)
            
            self.parent.statusBar().setStyleSheet("color: green;")
            self.parent.statusBar().showMessage("New book selected!", 6000)