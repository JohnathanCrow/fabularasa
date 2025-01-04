"""Module for managing book tables and lists."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QHeaderView)
from utils.dates import get_current_date
from utils.db import write_csv_file

def create_book_table(include_date_added=False, include_read_date=False):
    """Create and configure a table widget for books."""
    table = QTableWidget()
    
    # Hide the vertical header (row numbers)
    table.verticalHeader().setVisible(False)
    
    headers = ["Title", "Author", "Words", "Rating", "Member"]
    if include_date_added:
        headers.append("Date Added")
    if include_read_date:
        headers.append("Read Date")
    
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    
    # Enable sorting
    table.setSortingEnabled(True)
    
    header = table.horizontalHeader()
    for i in range(len(headers)):
        header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Custom sort roles for numeric and date columns
        #if headers[i] in ["Words", "Rating"]:
        #    table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignRight)
    
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
        
        # Date fields - check header text to determine which date to show
        if table.columnCount() > 5:  # If there's a date column
            header_text = table.horizontalHeaderItem(5).text()
            if header_text == "Date Added":
                date_item = QTableWidgetItem()
                date_item.setData(Qt.ItemDataRole.DisplayRole, book["date_added"])
                date_item.setData(Qt.ItemDataRole.EditRole, book["date_added"])
                table.setItem(row, 5, date_item)
            else:  # Read Date column
                date_item = QTableWidgetItem()
                date_item.setData(Qt.ItemDataRole.DisplayRole, book.get("read_date", ""))
                date_item.setData(Qt.ItemDataRole.EditRole, book.get("read_date", ""))
                table.setItem(row, 5, date_item)
    
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
        self.selected_table = create_book_table(include_read_date=True)
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

        # Import the necessary functions
        from utils.selection import calculate_scores, calculate_book_score

        # Store the imported functions as instance variables
        self.calculate_scores = calculate_scores
        self.calculate_book_score = calculate_book_score
    
    def _setup_default_sorting(self):
        """Set up default sorting for both tables."""
        # Sort unselected table by Date Added (column 5) in descending order
        self.unselected_table.sortItems(5, Qt.SortOrder.DescendingOrder)
        
        # Sort selected table by Read Date (column 5) in descending order
        self.selected_table.sortItems(5, Qt.SortOrder.DescendingOrder)
    
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
                "date_added": self.unselected_table.item(row, 5).text() if self.unselected_table.item(row, 5) else get_current_date(),
                "read_date": "",
                "score": 0  # Will be calculated below
            }
            # Calculate score for this book
            book["score"] = self.calculate_book_score(book)
            books.append(book)
        
        # Process selected table
        for row in range(self.selected_table.rowCount()):
            book = {
                "title": self.selected_table.item(row, 0).text() if self.selected_table.item(row, 0) else "",
                "author": self.selected_table.item(row, 1).text() if self.selected_table.item(row, 1) else "",
                "length": int(self.selected_table.item(row, 2).text()) if self.selected_table.item(row, 2) else 0,
                "rating": float(self.selected_table.item(row, 3).text()) if self.selected_table.item(row, 3) else 0.0,
                "member": self.selected_table.item(row, 4).text() if self.selected_table.item(row, 4) else "",
                "date_added": get_current_date(),
                "read_date": self.selected_table.item(row, 5).text() if self.selected_table.item(row, 5) else "",
                "score": 0  # Will be calculated below
            }
            # Calculate score for this book
            book["score"] = self.calculate_book_score(book)
            books.append(book)

        # Calculate all scores considering member selection history
        books = self.calculate_scores(books)

        headers = ["title", "author", "length", "rating", "member", "score", 
                  "date_added", "read_date"]
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
        
        # Set default date_added for the new row
        date_col = 5  # Index of the date_added column
        date_item = QTableWidgetItem(get_current_date())
        self.unselected_table.setItem(self.unselected_table.rowCount() - 1, date_col, date_item)
    
    def load_books(self, books):
        """Load and split books between the two tables."""
        if not books:
            return
        
        # Calculate scores before splitting the books
        books = self.calculate_scores(books)
            
        selected = [b for b in books if b.get("read_date")]
        unselected = [b for b in books if not b.get("read_date")]
        
        # Clear existing data
        self.unselected_table.setRowCount(0)
        self.selected_table.setRowCount(0)
        
        populate_table(self.unselected_table, unselected)
        populate_table(self.selected_table, selected)
        
        # Set up default sorting after populating tables
        self._setup_default_sorting()