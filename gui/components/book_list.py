from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

from utils.books.selection import calculate_book_score, calculate_scores
from utils.core.dates import get_current_date
from utils.core.db import read_db, write_db
from utils.core.isbn import validate_isbn


class BookTableItem(QTableWidgetItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.original_text = text

    def setData(self, role: int, value: any) -> None:
        if role == Qt.ItemDataRole.EditRole and self.column() == 2 and value:
            if cleaned_isbn := validate_isbn(value):
                value = cleaned_isbn
        super().setData(role, value)


def create_book_table(include_date_added=False, include_read_date=False):
    table = QTableWidget()
    table.verticalHeader().setVisible(False)

    headers = ["Title", "Author", "ISBN", "Words", "Rating", "Member"]
    if include_date_added:
        headers.append("Date Added")
    if include_read_date:
        headers.append("Read Date")

    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setSortingEnabled(True)

    header = table.horizontalHeader()
    for i in range(len(headers)):
        header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    return table


def populate_table(table, books):
    table.setSortingEnabled(False)
    table.setRowCount(len(books))

    for row, book in enumerate(books):
        table.setItem(row, 0, QTableWidgetItem(book["title"]))
        table.setItem(row, 1, QTableWidgetItem(book["author"]))

        # Use custom table item for ISBN
        isbn_item = BookTableItem(book.get("isbn", ""))
        if isbn_item.text():
            if cleaned_isbn := validate_isbn(isbn_item.text()):
                isbn_item.setText(cleaned_isbn)
        table.setItem(row, 2, isbn_item)

        words_item = QTableWidgetItem()
        words_item.setData(Qt.ItemDataRole.DisplayRole, str(book["length"]))
        words_item.setData(Qt.ItemDataRole.EditRole, int(book["length"]))
        table.setItem(row, 3, words_item)

        rating_item = QTableWidgetItem()
        rating_item.setData(Qt.ItemDataRole.DisplayRole, str(book["rating"]))
        rating_item.setData(Qt.ItemDataRole.EditRole, float(book["rating"]))
        table.setItem(row, 4, rating_item)

        table.setItem(row, 5, QTableWidgetItem(book["member"]))

        if table.columnCount() > 6:
            header_text = table.horizontalHeaderItem(6).text()
            date_item = QTableWidgetItem()
            if header_text == "Date Added":
                date_item.setData(Qt.ItemDataRole.DisplayRole, book["date_added"])
                date_item.setData(Qt.ItemDataRole.EditRole, book["date_added"])
            else:
                date_item.setData(
                    Qt.ItemDataRole.DisplayRole, book.get("read_date", "")
                )
                date_item.setData(Qt.ItemDataRole.EditRole, book.get("read_date", ""))
            table.setItem(row, 6, date_item)

    table.setSortingEnabled(True)


class BookListWidget(QWidget):
    saved = pyqtSignal()

    def __init__(self, profile_manager=None):
        super().__init__()
        self.profile_manager = profile_manager
        self.calculate_scores = calculate_scores
        self.calculate_book_score = calculate_book_score
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)

        layout.addWidget(QLabel("Available Books"))
        self.unselected_table = create_book_table(include_date_added=True)
        layout.addWidget(self.unselected_table)

        layout.addWidget(QLabel("Selected Books"))
        self.selected_table = create_book_table(include_read_date=True)
        layout.addWidget(self.selected_table)

        button_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add_row)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_changes)

        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

    def closeEvent(self, event):
        if hasattr(self, "unselected_table"):
            self.unselected_table.clear()
            self.unselected_table.deleteLater()
        if hasattr(self, "selected_table"):
            self.selected_table.clear()
            self.selected_table.deleteLater()
        if hasattr(self, "remove_btn"):
            self.remove_btn.deleteLater()
        if hasattr(self, "add_btn"):
            self.add_btn.deleteLater()
        if hasattr(self, "save_btn"):
            self.save_btn.deleteLater()
        super().closeEvent(event)

    def _setup_default_sorting(self):
        self.unselected_table.sortItems(6, Qt.SortOrder.DescendingOrder)
        self.selected_table.sortItems(6, Qt.SortOrder.DescendingOrder)

    def _save_changes(self):
        profile = (
            self.profile_manager.get_current_profile() if self.profile_manager else None
        )
        books = []

        # Process unselected table
        for row in range(self.unselected_table.rowCount()):
            book = {
                "title": (
                    self.unselected_table.item(row, 0).text()
                    if self.unselected_table.item(row, 0)
                    else ""
                ),
                "author": (
                    self.unselected_table.item(row, 1).text()
                    if self.unselected_table.item(row, 1)
                    else ""
                ),
                "isbn": (
                    self.unselected_table.item(row, 2).text()
                    if self.unselected_table.item(row, 2)
                    else ""
                ),
                "length": (
                    int(self.unselected_table.item(row, 3).text())
                    if self.unselected_table.item(row, 3)
                    else 0
                ),
                "rating": (
                    float(self.unselected_table.item(row, 4).text())
                    if self.unselected_table.item(row, 4)
                    else 0.0
                ),
                "member": (
                    self.unselected_table.item(row, 5).text()
                    if self.unselected_table.item(row, 5)
                    else ""
                ),
                "date_added": (
                    self.unselected_table.item(row, 6).text()
                    if self.unselected_table.item(row, 6)
                    else get_current_date()
                ),
                "read_date": "",
                "score": 0,
            }
            if any(book.values()):
                book["score"] = self.calculate_book_score(book)
                books.append(book)

        # Process selected table
        for row in range(self.selected_table.rowCount()):
            book = {
                "title": (
                    self.selected_table.item(row, 0).text()
                    if self.selected_table.item(row, 0)
                    else ""
                ),
                "author": (
                    self.selected_table.item(row, 1).text()
                    if self.selected_table.item(row, 1)
                    else ""
                ),
                "isbn": (
                    self.selected_table.item(row, 2).text()
                    if self.selected_table.item(row, 2)
                    else "N/A"
                ),
                "length": (
                    int(self.selected_table.item(row, 3).text())
                    if self.selected_table.item(row, 3)
                    else 0
                ),
                "rating": (
                    float(self.selected_table.item(row, 4).text())
                    if self.selected_table.item(row, 4)
                    else 0.0
                ),
                "member": (
                    self.selected_table.item(row, 5).text()
                    if self.selected_table.item(row, 5)
                    else ""
                ),
                "date_added": get_current_date(),
                "read_date": (
                    self.selected_table.item(row, 6).text()
                    if self.selected_table.item(row, 6)
                    else ""
                ),
                "score": 0,
            }
            if any(book.values()):
                book["score"] = self.calculate_book_score(book)
                books.append(book)

        books = self.calculate_scores(books)

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
        write_db(books, profile)

        self.saved.emit()

    def _remove_selected(self):
        for table in [self.unselected_table, self.selected_table]:
            rows = sorted({item.row() for item in table.selectedItems()}, reverse=True)
            for row in rows:
                table.removeRow(row)

    def _add_row(self):
        self.unselected_table.insertRow(self.unselected_table.rowCount())
        date_col = 6  # Updated column index for date_added
        date_item = QTableWidgetItem(get_current_date())
        self.unselected_table.setItem(
            self.unselected_table.rowCount() - 1, date_col, date_item
        )

    def load_books(self, books):
        profile = (
            self.profile_manager.get_current_profile() if self.profile_manager else None
        )

        self.unselected_table.setRowCount(0)
        self.selected_table.setRowCount(0)

        if not books:
            return

        books = self.calculate_scores(books)
        selected = [b for b in books if b.get("read_date")]
        unselected = [b for b in books if not b.get("read_date")]

        populate_table(self.unselected_table, unselected)
        populate_table(self.selected_table, selected)

        self._setup_default_sorting()
