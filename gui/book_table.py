"""Module for managing book tables and lists."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QHeaderView)
from utils.dates import get_current_date
from utils.db import write_csv_file

def create_book_table(include_date_added=False, include_date_selected=False):
    """Create and configure a table widget for books."""
    table = QTableWidget()
    
    headers = ["Title", "Author", "Words", "Rating", "Member"]
    if include_date_added:
        headers.append("Date Added")
    if include_date_selected:
        headers.append("Date Selected")
    
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    
    # Enable sorting
    table.setSortingEnabled(True)
    
    header = table.horizontalHeader()
    for i in range(len(headers)):
        header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Custom sort roles for numeric and date columns
        if headers[i] in ["Words", "Rating"]:
            table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignRight)
    
    return table

def populate_table(table, books):
    """Populate a table with book data."""
    # Temporarily disable sorting while populating
    table.setSortingEnabled(False)
    
    table.setRowCount(len(books))
    for row, book in enumerate(books):
        # Title, Author, Member (text items)
        table.setItem(row, 0, QTableWidgetItem(book["title"]))
        table.setItem(row, 1, QTableWidgetItem(book["author"]))
        table.setItem(row, 4, QTableWidgetItem(book["member"]))
        
        # Words (numeric)
        words_item = QTableWidgetItem()
        words_item.setData(Qt.ItemDataRole.DisplayRole, str(book["length"]))
        words_item.setData(Qt.ItemDataRole.EditRole, int(book["length"]))
        table.setItem(row, 2, words_item)
        
        # Rating (numeric)
        rating_item = QTableWidgetItem()
        rating_item.setData(Qt.ItemDataRole.DisplayRole, str(book["rating"]))
        rating_item.setData(Qt.ItemDataRole.EditRole, float(book["rating"]))
        table.setItem(row, 3, rating_item)
        
        # Dates
        col = 5
        if "date_added" in book and table.columnCount() > col:
            date_item = QTableWidgetItem()
            date_item.setData(Qt.ItemDataRole.DisplayRole, book["date_added"])
            date_item.setData(Qt.ItemDataRole.EditRole, book["date_added"])
            table.setItem(row, col, date_item)
            col += 1
            
        if "date_selected" in book and table.columnCount() > col:
            date_item = QTableWidgetItem()
            date_item.setData(Qt.ItemDataRole.DisplayRole, book["date_selected"])
            date_item.setData(Qt.ItemDataRole.EditRole, book["date_selected"])
            table.setItem(row, col, date_item)
    
    # Re-enable sorting after populating
    table.setSortingEnabled(True)

class BookListWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        
        layout.addWidget(QLabel("Available Books"))
        self.unselected_table = create_book_table(include_date_added=True)
        layout.addWidget(self.unselected_table)
        
        layout.addWidget(QLabel("Selected Books"))
        self.selected_table = create_book_table(include_date_selected=True)
        layout.addWidget(self.selected_table)
        
        button_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove Entry")
        remove_btn.clicked.connect(self._remove_selected)
        add_btn = QPushButton("Add Entry")
        add_btn.clicked.connect(self._add_row)
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self._save_changes)
        
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(add_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
    def _save_changes(self):
        """Save all changes to the CSV file."""
        books = []
        
        # Process unselected table
        for row in range(self.unselected_table.rowCount()):
            book = {
                "title": self.unselected_table.item(row, 0).text() if self.unselected_table.item(row, 0) else "",
                "author": self.unselected_table.item(row, 1).text() if self.unselected_table.item(row, 1) else "",
                "length": int(self.unselected_table.item(row, 2).text()) if self.unselected_table.item(row, 2) else 0,
                "rating": float(self.unselected_table.item(row, 3).text()) if self.unselected_table.item(row, 3) else 0.0,
                "member": self.unselected_table.item(row, 4).text() if self.unselected_table.item(row, 4) else "",
                "score": 0,
                "date_added": self.unselected_table.item(row, 5).text() if self.unselected_table.item(row, 5) else get_current_date(),
                "date_selected": ""
            }
            books.append(book)
        
        # Process selected table
        for row in range(self.selected_table.rowCount()):
            date_selected = self.selected_table.item(row, 6).text() if self.selected_table.columnCount() > 6 and self.selected_table.item(row, 6) else get_current_date()
            book = {
                "title": self.selected_table.item(row, 0).text() if self.selected_table.item(row, 0) else "",
                "author": self.selected_table.item(row, 1).text() if self.selected_table.item(row, 1) else "",
                "length": int(self.selected_table.item(row, 2).text()) if self.selected_table.item(row, 2) else 0,
                "rating": float(self.selected_table.item(row, 3).text()) if self.selected_table.item(row, 3) else 0.0,
                "member": self.selected_table.item(row, 4).text() if self.selected_table.item(row, 4) else "",
                "score": 0,
                "date_added": self.selected_table.item(row, 5).text() if self.selected_table.item(row, 5) else get_current_date(),
                "date_selected": date_selected
            }
            books.append(book)

        headers = ["title", "author", "length", "rating", "member", "score", 
                  "date_added", "date_selected"]
        write_csv_file("books.csv", books, headers)
    
    def _remove_selected(self):
        """Remove selected rows from either table."""
        for table in [self.unselected_table, self.selected_table]:
            rows = sorted(set(item.row() for item in table.selectedItems()), reverse=True)
            for row in rows:
                table.removeRow(row)
    
    def _add_row(self):
        """Add a new empty row to the unselected table."""
        self.unselected_table.insertRow(self.unselected_table.rowCount())
    
    def load_books(self, books):
        """Load and split books between the two tables."""
        if not books:
            return
            
        selected = [b for b in books if b.get("date_selected")]
        unselected = [b for b in books if not b.get("date_selected")]
        
        populate_table(self.unselected_table, unselected)
        populate_table(self.selected_table, selected)