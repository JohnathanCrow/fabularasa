"""Module for managing book tables and lists."""
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
    
    header = table.horizontalHeader()
    for i in range(len(headers)):
        header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
    return table

def populate_table(table, books):
    """Populate a table with book data."""
    table.setRowCount(len(books))
    for row, book in enumerate(books):
        table.setItem(row, 0, QTableWidgetItem(book["title"]))
        table.setItem(row, 1, QTableWidgetItem(book["author"]))
        table.setItem(row, 2, QTableWidgetItem(str(book["length"])))
        table.setItem(row, 3, QTableWidgetItem(str(book["rating"])))
        table.setItem(row, 4, QTableWidgetItem(book["member"]))
        
        col = 5
        if "date_added" in book and table.columnCount() > col:
            table.setItem(row, col, QTableWidgetItem(book["date_added"]))
            col += 1
        if "date_selected" in book and table.columnCount() > col:
            table.setItem(row, col, QTableWidgetItem(book["date_selected"]))

class BookListWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Available Books"))
        self.unselected_table = create_book_table(include_date_added=True)
        layout.addWidget(self.unselected_table)
        
        layout.addWidget(QLabel("Selected Books"))
        self.selected_table = create_book_table(include_date_selected=True)
        layout.addWidget(self.selected_table)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self._save_changes)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_selected)
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self._add_row)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)
        
    def _save_changes(self):
        """Save all changes to the CSV file."""
        books = []
        
        for table in [self.unselected_table, self.selected_table]:
            for row in range(table.rowCount()):
                date_selected = ""
                if table == self.selected_table:
                    date_selected = table.item(row, 6).text() if table.columnCount() > 6 and table.item(row, 6) else get_current_date()
                
                book = {
                    "title": table.item(row, 0).text() if table.item(row, 0) else "",
                    "author": table.item(row, 1).text() if table.item(row, 1) else "",
                    "length": table.item(row, 2).text() if table.item(row, 2) else "0",
                    "rating": table.item(row, 3).text() if table.item(row, 3) else "0",
                    "member": table.item(row, 4).text() if table.item(row, 4) else "",
                    "score": "0",
                    "date_added": table.item(row, 5).text() if table.item(row, 5) else get_current_date(),
                    "date_selected": date_selected
                }
                if book["title"] and book["author"]:
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