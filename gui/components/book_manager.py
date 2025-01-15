import json
from datetime import datetime

from PyQt6.QtCore import Qt, QUrl, QDate
from PyQt6.QtGui import QDesktopServices, QFont, QIcon, QPixmap, QTextCharFormat, QColor
from PyQt6.QtWidgets import QHBoxLayout, QListWidgetItem, QPushButton, QWidget

from utils.books.scraping import GoodreadsClient
from utils.books.selection import (calculate_scores, get_selected_books,
                                   select_top_choice)
from utils.common.constants import DATE_FORMAT
from utils.core.dates import format_date, get_current_date, get_next_monday
from utils.core.db import read_db, write_db
from utils.core.isbn import validate_isbn
from utils.core.paths import get_data_dir, get_state_file_path, resource_path


class BookManager:
    def __init__(self, parent):
        self.parent = parent
        self.profile_manager = parent.profile_manager if parent else None
        self.book_input = None
        self.author_input = None
        self.word_count_input = None
        self.member_input = None
        self.selected_list = None
        self.cover_label = None
        self.details_label = None
        self.title_label = None
        self.book_list_widget = None
        self.goodreads_client = GoodreadsClient()
        self.read_date_calendar = None
        self.current_book_index = 0
        self.selected_books = []
        self.nav_buttons = {}
        self.store_buttons = {}
        self.load_initial_data()
        
    def load_initial_data(self):
        if self.profile_manager:
            profile = self.profile_manager.get_current_profile()
            books = read_db(profile)
            self.selected_books = [b for b in books if b.get("read_date")]
            self.selected_books.sort(key=lambda x: x.get("read_date"), reverse=False)
            self.current_book_index = len(self.selected_books) - 1 if self.selected_books else 0

    def reload_data(self):
        profile = self.profile_manager.get_current_profile()

        if self.selected_list:
            self.selected_list.clear()

        if self.book_list_widget:
            books = read_db(profile)
            self.book_list_widget.load_books(books)

        self.update_selected_list()
        self.load_selected_books()
        self.update_current_selection()
        self.update_calendar_highlighting()  # Update calendar when data is reloaded

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
        books = read_db(profile)
        self.selected_books = [b for b in books if b.get("read_date")]
        # Sort in ascending order (oldest to newest)
        self.selected_books.sort(key=lambda x: x.get("read_date"), reverse=False)
        # Initialize to the last (most recent) book
        self.current_book_index = (
            len(self.selected_books) - 1 if self.selected_books else 0
        )
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
        if (
            self.selected_books
            and self.current_book_index < len(self.selected_books) - 1
        ):
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
            books = read_db(profile)
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
            if self.title_label:
                self.title_label.setText("Selected Book")
            return

        current_book = self.selected_books[self.current_book_index]
        self._update_cover(current_book)
        self._update_details(current_book)
        self.update_nav_buttons()

        if self.title_label:
            current_date = get_current_date()
            if book_date := current_book.get("read_date", ""):
                try:
                    formatted_date = datetime.strptime(book_date, DATE_FORMAT).strftime(
                        "%d %B, %Y"
                    )
                    self.title_label.setText(formatted_date)
                except ValueError:
                    self.title_label.setText("Selected Book")
            else:
                self.title_label.setText("Selected Book")

    def _update_cover(self, book):
        if self.cover_label:
            if pixmap := self.goodreads_client.get_cover(
                book["title"], 
                book["author"],  # Add the author parameter
                book.get("isbn")  # ISBN becomes the third parameter
            ):
                pixmap = pixmap.scaled(
                    self.cover_label.width(),
                    self.cover_label.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                )
                self.cover_label.setPixmap(pixmap)
            else:
                self._set_placeholder_cover()

    def _set_placeholder_cover(self):
        try:
            placeholder_path = "assets/no_cover.png"
            pixmap = QPixmap(placeholder_path)
            if pixmap.isNull():
                self.cover_label.setText("No cover found")
            else:
                pixmap = pixmap.scaled(
                    self.cover_label.width(),
                    self.cover_label.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                )
                self.cover_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error setting placeholder: {e}")
            self.cover_label.setText("No book selected")

    def _get_store_urls(self, book):
        # Load store settings
        try:
            with open(get_state_file_path("misc_settings.json"), "r") as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {"amazon_address": ".com", "kobo_region": "us/en"}

        # Goodreads URL (using existing client logic)
        goodreads_url = self.goodreads_client._get_book_page_url(
            book["title"], book.get("isbn")
        )

        # Amazon search URL with custom domain
        search_term = f"{book['title']} {book['author']}".replace(" ", "+")
        amazon_url = f"https://www.amazon{settings['amazon_address']}/s?k={search_term}"

        # Kobo store search URL with custom region
        kobo_url = (
            f"https://www.kobo.com/{settings['kobo_region']}/search?query={search_term}"
        )

        return {
            "goodreads": goodreads_url or "",
            "amazon": amazon_url,
            "kobo": kobo_url,
        }

    def _create_store_buttons(self):
        button_container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)

        # Create buttons for each store
        for store in ["goodreads", "amazon", "kobo"]:
            button = QPushButton(store.capitalize())
            button.setObjectName(f"{store}_button")
            button.clicked.connect(lambda checked, s=store: self._open_store_url(s))
            layout.addWidget(button)
            self.store_buttons[store] = button

        button_container.setLayout(layout)
        return button_container

    def _open_store_url(self, store):
        if not self.selected_books or self.current_book_index >= len(
            self.selected_books
        ):
            return

        current_book = self.selected_books[self.current_book_index]
        urls = self._get_store_urls(current_book)

        if urls[store]:
            QDesktopServices.openUrl(QUrl(urls[store]))

    def _update_details(self, book):
        if self.details_label:
            # <h2>{book['title']}</h2>
            details = f"""
            <p></p>
            <p><b>Author:</b> {book['author']}</p>
            <p><b>ISBN:</b> {book.get('isbn', 'N/A')}</p>
            <p><b>Words:</b> {book['length']}</p>
            <p><b>Rating:</b> {book['rating']}</p>
            <p><b>Score:</b> {book['score']}</p>
            <p><b>Member:</b> {book['member']}</p>

            """
            self.details_label.setText(details)

    def parse_word_count(self, word_count_str):
        try:
            if word_count_str.lower().endswith("k"):
                return int(float(word_count_str[:-1]) * 1000)
            return int(word_count_str)
        except ValueError as e:
            raise ValueError(f"Invalid word count format: {word_count_str}") from e

    def add_book(self):
            profile = self.profile_manager.get_current_profile()
            try:
                query = self.book_input.text().strip()
                word_count_str = self.word_count_input.text().strip()
                member = self.member_input.text().strip()

                if not query:
                    self.parent.statusBar().setStyleSheet("color: red;")
                    self.parent.statusBar().showMessage(
                        "Title/ISBN is required!", 6000
                    )
                    return

                # Check if query is ISBN
                isbn = validate_isbn(query)
                is_isbn_query = bool(isbn)

                metadata = self.goodreads_client.get_book_info(
                    query, isbn if is_isbn_query else None
                )
                
                if metadata:
                    pixmap = self.goodreads_client.get_cover(
                        metadata["title"],
                        metadata["author"],
                        isbn if is_isbn_query else metadata.get("isbn")
                    )
                    if pixmap:  # Ensure a cover was fetched
                        pixmap = pixmap.scaled(400, 600, Qt.AspectRatioMode.IgnoreAspectRatio)

                    
                    # Use manual word count if provided, otherwise use estimated
                    try:
                        word_count = self.parse_word_count(word_count_str) if word_count_str else metadata["length"]
                    except ValueError as e:
                        self.parent.statusBar().setStyleSheet("color: red;")
                        self.parent.statusBar().showMessage(str(e), 6000)
                        return

                    book_data = {
                        "title": metadata["title"],
                        "author": metadata["author"],
                        "isbn": isbn if is_isbn_query else metadata.get("isbn", ""),
                        "length": word_count,
                        "rating": float(metadata["rating"]),
                        "member": member,
                        "score": 0,
                        "date_added": get_current_date(),
                        "read_date": "",
                    }
                else:
                    if not word_count_str:
                        self.parent.statusBar().setStyleSheet("color: red;")
                        self.parent.statusBar().showMessage(
                            "Word count is required when book metadata cannot be found!", 6000
                        )
                        return

                    try:
                        word_count = self.parse_word_count(word_count_str)
                    except ValueError as e:
                        self.parent.statusBar().setStyleSheet("color: red;")
                        self.parent.statusBar().showMessage(str(e), 6000)
                        return

                    book_data = {
                        "title": "Unknown" if is_isbn_query else query,
                        "author": self.author_input.text().strip() or "Unknown",
                        "isbn": isbn if is_isbn_query else "",
                        "length": word_count,
                        "rating": 0.0,
                        "member": member,
                        "score": 0,
                        "date_added": get_current_date(),
                        "read_date": "",
                    }

                    # Try to cache cover even for manually added books
                    self.goodreads_client.get_cover(
                        book_data["title"],
                        book_data["author"],
                        book_data["isbn"] if book_data["isbn"] else None
                    )

                books = read_db(profile)
                books.append(book_data)
                books_with_scores = calculate_scores(books)

                self.write_books_to_db(books_with_scores, profile)
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
                
    def update_calendar_highlighting(self):
        if not hasattr(self, 'read_date_calendar'):
            return

        # Clear existing highlighting
        format = QTextCharFormat()
        self.read_date_calendar.setDateTextFormat(QDate(), format)

        # Get all books with read dates
        profile = self.profile_manager.get_current_profile() if self.profile_manager else None
        books = read_db(profile)
        read_dates = [book['read_date'] for book in books if book.get('read_date')]

        # Create highlighting format
        highlight_format = QTextCharFormat()
        highlight_format.setForeground(QColor('#1565c0'))  # Same blue as buttons

        # Apply highlighting to dates with books
        for date_str in read_dates:
            try:
                date = QDate.fromString(date_str, 'yyyy-MM-dd')
                if date.isValid():
                    self.read_date_calendar.setDateTextFormat(date, highlight_format)
            except Exception as e:
                print(f"Error highlighting date {date_str}: {e}")

    def select_book(self):
        profile = self.profile_manager.get_current_profile()
        books = read_db(profile)
        books = calculate_scores(books)

        if top_book := select_top_choice(books):
            self.update_selected_book_and_refresh(top_book, books, profile)
        else:
            self.parent.statusBar().setStyleSheet("color: red;")
            self.parent.statusBar().showMessage("No available books!", 6000)

    def update_selected_book_and_refresh(self, top_book, books, profile):
        selected_date = (
            self.read_date_calendar.selectedDate().toPyDate()
            if self.read_date_calendar and self.read_date_calendar.selectedDate()
            else get_next_monday()
        )
        top_book["read_date"] = format_date(selected_date)
        for book in books:
            if book["title"] == top_book["title"]:
                book["read_date"] = top_book["read_date"]

        self.write_books_to_db(books, profile)
        self.load_selected_books()
        self.update_selected_list()
        self.update_current_selection()
        self.update_calendar_highlighting()  # Update calendar after selecting a book

        self.parent.statusBar().setStyleSheet("color: green;")
        self.parent.statusBar().showMessage("New book selected!", 6000)

    def write_books_to_db(self, arg0, profile):
        headers = [
            "title",
            "author",
            "isbn",
            "length",
            "rating",
            "member",
            "score",
            "date_added",
            "read_date",
        ]
        write_db(arg0, profile)
        if self.book_list_widget:
            self.book_list_widget.load_books(arg0)
