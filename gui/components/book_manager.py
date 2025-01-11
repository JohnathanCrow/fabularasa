from PyQt6.QtWidgets import (QListWidgetItem, QHBoxLayout, QPushButton, 
                           QWidget)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
from utils.core.dates import get_next_monday, format_date, get_current_date
from utils.core.db import read_db, write_db
from utils.books.selection import (
    select_top_choice,
    get_selected_books,
    calculate_scores
)
from utils.books.scraping import GoodreadsClient
from utils.core.paths import resource_path

class BookManager:
    def __init__(self, parent):
        self.parent = parent
        self.profile_manager = parent.profile_manager
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
        self.current_book_index = 0
        self.selected_books = []
        self.nav_buttons = {}

    def reload_data(self):
        profile = self.profile_manager.get_current_profile()
        
        if self.selected_list:
            self.selected_list.clear()
            
        if self.book_list_widget:
            books = read_db("books.db", profile)
            self.book_list_widget.load_books(books)
        
        self.update_selected_list()
        self.load_selected_books()
        self.update_current_selection()
        
        if self.book_input:
            self.book_input.clear()
        if self.author_input:
            self.author_input.clear()
        if self.word_count_input:
            self.word_count_input.clear()
        if self.member_input:
            self.member_input.clear()

    def load_selected_books(self):
        profile = self.profile_manager.get_current_profile()
        books = read_db("books.db", profile)
        self.selected_books = [b for b in books if b.get("read_date")]
        # Sort in ascending order (oldest to newest)
        self.selected_books.sort(key=lambda x: x.get("read_date"), reverse=False)
        # Initialize to the last (most recent) book
        self.current_book_index = len(self.selected_books) - 1 if self.selected_books else 0
        self.update_nav_buttons()

    def update_nav_buttons(self):
        if not self.nav_buttons:
            return
            
        has_books = bool(self.selected_books)
        not_first = self.current_book_index > 0
        not_last = self.current_book_index < len(self.selected_books) - 1
        
        self.nav_buttons["first"].setEnabled(has_books and not_first)
        self.nav_buttons["prev"].setEnabled(has_books and not_first)
        self.nav_buttons["next"].setEnabled(has_books and not_last)
        self.nav_buttons["last"].setEnabled(has_books and not_last)
        self.nav_buttons["current"].setEnabled(has_books)

    def navigate_to_first(self):
        if self.selected_books:
            self.current_book_index = 0
            self.update_current_selection()

    def navigate_to_last(self):
        if self.selected_books:
            self.current_book_index = len(self.selected_books) - 1
            self.update_current_selection()

    def navigate_to_prev(self):
        if self.selected_books and self.current_book_index > 0:
            self.current_book_index -= 1
            self.update_current_selection()

    def navigate_to_next(self):
        if self.selected_books and self.current_book_index < len(self.selected_books) - 1:
            self.current_book_index += 1
            self.update_current_selection()

    def navigate_to_current(self):
        if self.selected_books:
            current_date = get_current_date()
            for i in range(len(self.selected_books) - 1, -1, -1):
                if self.selected_books[i]["read_date"] <= current_date:
                    self.current_book_index = i
                    self.update_current_selection()
                    break

    def update_selected_list(self):
        if self.selected_list:
            self.selected_list.clear()
            profile = self.profile_manager.get_current_profile()
            books = read_db("books.db", profile)
            selected_books = [b for b in books if b.get("read_date")]
            # Keep the display list in descending order (newest to oldest)
            selected_books.sort(key=lambda x: x.get("read_date"), reverse=True)
            
            for book in selected_books[:20]:
                text = f"{book['title']}, {book['author']} ({book['member']})"
                item = QListWidgetItem(text)
                item.setFont(QFont())
                self.selected_list.addItem(item)

    def update_current_selection(self):
        if not self.selected_books:
            if self.cover_label:
                self._set_placeholder_cover()
            if self.details_label:
                self.details_label.setText("")
            return

        current_book = self.selected_books[self.current_book_index]
        self._update_cover(current_book)
        self._update_details(current_book)
        self.update_nav_buttons()

    def _update_cover(self, book):
        if self.cover_label:
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
        try:
            placeholder_path = "assets/no_cover.png"
            pixmap = QPixmap(placeholder_path)
            if pixmap.isNull():
                self.cover_label.setText("No book selected")
            else:
                pixmap = pixmap.scaled(
                    self.cover_label.width(),
                    self.cover_label.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio
                )
                self.cover_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error setting placeholder: {e}")
            self.cover_label.setText("No book selected")

    def _update_details(self, book):
        if self.details_label:
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
        try:
            if word_count_str.lower().endswith("k"):
                return int(float(word_count_str[:-1]) * 1000)
            return int(word_count_str)
        except ValueError:
            raise ValueError(f"Invalid word count format: {word_count_str}")

    def add_book(self):
        profile = self.profile_manager.get_current_profile()
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

            books = read_db("books.db", profile)
            books.append(book_data)
            books_with_scores = calculate_scores(books)
            
            headers = ["title", "author", "length", "rating", "member", "score", 
                      "date_added", "read_date"]
            write_db("books.db", books_with_scores, headers, profile)
            
            if self.book_list_widget:
                self.book_list_widget.load_books(books_with_scores)
            
            self.book_input.clear()
            self.author_input.clear()
            self.word_count_input.clear()
            self.member_input.clear()
            self.book_input.setFocus()
            
            self.parent.statusBar().setStyleSheet("color: green;")
            self.parent.statusBar().showMessage("Book added successfully!", 6000)
        except Exception as e:
            print(f"Error adding book: {e}")
            self.parent.statusBar().setStyleSheet("color: red;")
            self.parent.statusBar().showMessage(f"Error adding book: {str(e)}", 6000)

    def select_book(self):
        profile = self.profile_manager.get_current_profile()
        books = read_db("books.db", profile)
        books = calculate_scores(books)
        
        top_book = select_top_choice(books)
        if top_book:
            if self.read_date_calendar and self.read_date_calendar.selectedDate():
                selected_date = self.read_date_calendar.selectedDate().toPyDate()
                top_book["read_date"] = format_date(selected_date)
            else:
                selected_date = get_next_monday()
                top_book["read_date"] = format_date(selected_date)
            
            for book in books:
                if book["title"] == top_book["title"]:
                    book["read_date"] = top_book["read_date"]
            
            headers = ["title", "author", "length", "rating", "member", "score", 
                      "date_added", "read_date"]
            write_db("books.db", books, headers, profile)
            
            if self.book_list_widget:
                self.book_list_widget.load_books(books)
            
            self.load_selected_books()
            self.update_selected_list()
            self.update_current_selection()
            
            self.parent.statusBar().setStyleSheet("color: green;")
            self.parent.statusBar().showMessage("New book selected!", 6000)
        else:
            self.parent.statusBar().setStyleSheet("color: red;")
            self.parent.statusBar().showMessage("No available books!", 6000)