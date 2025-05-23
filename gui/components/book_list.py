from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QHeaderView, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QVBoxLayout, QListWidget,
                            QWidget, QLineEdit, QInputDialog, QStyledItemDelegate,
                            QMenu, QCalendarWidget, QMessageBox)
from PyQt6.QtGui import QAction

from utils.books.selection import calculate_book_score, calculate_scores
from utils.core.dates import get_current_date
from utils.core.db import read_db, write_db
from utils.core.isbn import validate_isbn

class TagItemDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() == 3:  # Tags column
            return None
        return super().createEditor(parent, option, index)

class TagEditorDialog(QDialog):
    def __init__(self, tags_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Tags")
        self.setModal(True)
        self.setMinimumWidth(300)
        
        self.tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
        
        layout = QVBoxLayout(self)
        
        # Tag list
        self.tag_list = QListWidget()
        self.refresh_tag_list()
        layout.addWidget(self.tag_list)
        
        # Input field
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter new tag...")
        self.tag_input.returnPressed.connect(self.add_tag)
        layout.addWidget(self.tag_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_tag)
        
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_tag)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_tag)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(rename_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def refresh_tag_list(self):
        self.tag_list.clear()
        for tag in sorted(self.tags):
            self.tag_list.addItem(tag)
            
    def add_tag(self):
        new_tag = self.tag_input.text().strip()
        if new_tag and new_tag not in self.tags:
            self.tags.append(new_tag)
            self.refresh_tag_list()
            self.tag_input.clear()
            
    def rename_tag(self):
        current_item = self.tag_list.currentItem()
        if not current_item:
            return
            
        old_tag = current_item.text()
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Rename Tag")
        dialog.setLabelText("New name:")
        dialog.setTextValue(old_tag)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_tag = dialog.textValue().strip()
            if new_tag and new_tag != old_tag:
                self.tags.remove(old_tag)
                self.tags.append(new_tag)
                self.refresh_tag_list()
                
    def delete_tag(self):
        current_item = self.tag_list.currentItem()
        if not current_item:
            return
            
        tag = current_item.text()
        self.tags.remove(tag)
        self.refresh_tag_list()
        
    def get_tags_string(self):
        return ", ".join(sorted(self.tags))

# Modify the BookTableItem class to handle tag editing
class BookTableItem(QTableWidgetItem):
    def __init__(self, text="", is_tag_column=False):
        super().__init__(text)
        self.original_text = text
        self.is_tag_column = is_tag_column
        self.tags_list = []
        if is_tag_column:
            self.setData(Qt.ItemDataRole.EditRole, text)

    def setData(self, role: int, value: any) -> None:
        if self.is_tag_column:
            if role == Qt.ItemDataRole.EditRole:
                # Store the actual tags string but display the count
                self.original_text = value
                self.tags_list = [tag.strip() for tag in value.split(",")] if value else []
                tag_count = len(self.tags_list) if self.tags_list else 0
                display_text = f"{tag_count} tags" if tag_count != 1 else "1 tag"
                super().setData(Qt.ItemDataRole.DisplayRole, display_text)
            elif role == Qt.ItemDataRole.UserRole:
                # Store the full tags string for reference
                self.original_text = value
        else:
            super().setData(role, value)

    def get_tags_string(self):
        return self.original_text

# Create a custom QTableWidgetItem for numerical sorting
class NumericTableItem(QTableWidgetItem):
    def __init__(self, value=0):
        super().__init__()
        self.setData(Qt.ItemDataRole.EditRole, value)
        
    def __lt__(self, other):
        # Compare by actual numeric value for sorting
        my_value = self.data(Qt.ItemDataRole.EditRole)
        other_value = other.data(Qt.ItemDataRole.EditRole)
        
        # Make sure we're comparing numbers
        try:
            return float(my_value) < float(other_value)
        except (ValueError, TypeError):
            return super().__lt__(other)

# Create a custom calendar widget with no week numbers and no weekend coloring
class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Remove week numbers
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        
        # Remove weekend coloring (Saturday and Sunday)
        format = self.weekdayTextFormat(Qt.DayOfWeek.Saturday)
        format.setForeground(self.weekdayTextFormat(Qt.DayOfWeek.Monday).foreground())
        self.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, format)
        self.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, format)

class DateSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")
        self.setModal(True)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Use our custom calendar widget
        self.calendar = CustomCalendarWidget()
        
        # Set initial date if provided
        if initial_date:
            try:
                from PyQt6.QtCore import QDate
                qdate = QDate.fromString(initial_date, "yyyy-MM-dd")
                if qdate.isValid():
                    self.calendar.setSelectedDate(qdate)
            except:
                pass
                
        layout.addWidget(self.calendar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
    
    def get_selected_date(self):
        return self.calendar.selectedDate().toString("yyyy-MM-dd")

def create_book_table(include_date_added=False, include_read_date=False):
    table = QTableWidget()
    table.verticalHeader().setVisible(False)

    # Set the custom delegate
    delegate = TagItemDelegate(table)
    table.setItemDelegate(delegate)

    headers = ["Title", "Author", "ISBN", "Tags", "Words", "Rating", "Member"]
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

    # Set up double-click handling for tags
    table.cellDoubleClicked.connect(lambda row, col: handle_cell_double_click(table, row, col))
    
    # Enable context menu for both tables
    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    return table

def handle_cell_double_click(table, row, col):
    # Get the header text to determine what kind of column this is
    header_item = table.horizontalHeaderItem(col)
    if not header_item:
        return
        
    header_text = header_item.text()
    
    # Handle tags column
    if col == 3:  # Tags column
        item = table.item(row, col)
        if item:
            dialog = TagEditorDialog(item.get_tags_string(), table)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_tags = dialog.get_tags_string()
                item.setData(Qt.ItemDataRole.EditRole, new_tags)
    
    # Handle date columns
    elif header_text in ["Date Added", "Read Date"]:
        item = table.item(row, col)
        current_date = item.text() if item else ""
        dialog = DateSelectionDialog(table, current_date)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_date = dialog.get_selected_date()
            date_item = QTableWidgetItem(new_date)
            date_item.setData(Qt.ItemDataRole.EditRole, new_date)
            table.setItem(row, col, date_item)

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

        # Create tag item with special handling
        tags = book.get("tags", "")
        tags_item = BookTableItem(tags, is_tag_column=True)
        # Explicitly set the data to trigger the display format
        tags_item.setData(Qt.ItemDataRole.EditRole, tags)
        table.setItem(row, 3, tags_item)

        # Use the custom NumericTableItem for proper numeric sorting
        word_count = int(book["length"]) if book["length"] else 0
        words_item = NumericTableItem(word_count)
        words_item.setData(Qt.ItemDataRole.DisplayRole, str(word_count))
        table.setItem(row, 4, words_item)

        # Use the custom NumericTableItem for rating as well
        rating_value = float(book["rating"]) if book["rating"] else 0.0
        rating_item = NumericTableItem(rating_value)
        rating_item.setData(Qt.ItemDataRole.DisplayRole, str(rating_value))
        table.setItem(row, 5, rating_item)

        table.setItem(row, 6, QTableWidgetItem(book["member"]))

        if table.columnCount() > 7:
            header_text = table.horizontalHeaderItem(7).text()
            date_item = QTableWidgetItem()
            if header_text == "Date Added":
                date_item.setData(Qt.ItemDataRole.DisplayRole, book["date_added"])
                date_item.setData(Qt.ItemDataRole.EditRole, book["date_added"])
            else:
                date_item.setData(Qt.ItemDataRole.DisplayRole, book.get("read_date", ""))
                date_item.setData(Qt.ItemDataRole.EditRole, book.get("read_date", ""))
            table.setItem(row, 7, date_item)

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
        self.unselected_table.customContextMenuRequested.connect(self._show_unselected_context_menu)
        layout.addWidget(self.unselected_table)

        layout.addWidget(QLabel("Selected Books"))
        self.selected_table = create_book_table(include_read_date=True)
        self.selected_table.customContextMenuRequested.connect(self._show_selected_context_menu)
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
        self.unselected_table.sortItems(7, Qt.SortOrder.DescendingOrder)
        self.selected_table.sortItems(7, Qt.SortOrder.DescendingOrder)
        
    def _show_unselected_context_menu(self, pos):
        global_pos = self.unselected_table.mapToGlobal(pos)
        
        # Get the row under the cursor
        row = self.unselected_table.rowAt(pos.y())
        if row < 0:
            return
            
        # Select the row
        self.unselected_table.selectRow(row)
        
        menu = QMenu()
        select_action = QAction("Select Book", self)
        select_action.triggered.connect(lambda: self._select_book(row))
        menu.addAction(select_action)
        
        remove_action = QAction("Remove Book", self)
        remove_action.triggered.connect(lambda: self._remove_book(self.unselected_table, row))
        menu.addAction(remove_action)
        
        menu.exec(global_pos)
        
    def _show_selected_context_menu(self, pos):
        global_pos = self.selected_table.mapToGlobal(pos)
        
        # Get the row under the cursor
        row = self.selected_table.rowAt(pos.y())
        if row < 0:
            return
            
        # Select the row
        self.selected_table.selectRow(row)
        
        menu = QMenu()
        deselect_action = QAction("Deselect Book", self)
        deselect_action.triggered.connect(lambda: self._deselect_book(row))
        menu.addAction(deselect_action)
        
        remove_action = QAction("Remove Book", self)
        remove_action.triggered.connect(lambda: self._remove_book(self.selected_table, row))
        menu.addAction(remove_action)
        
        menu.exec(global_pos)
    
    def _extract_book_data(self, table, row):
        """Extract book data from a table row"""
        book = {
            "title": table.item(row, 0).text() if table.item(row, 0) else "",
            "author": table.item(row, 1).text() if table.item(row, 1) else "",
            "isbn": table.item(row, 2).text() if table.item(row, 2) else "",
            "tags": table.item(row, 3).get_tags_string() if table.item(row, 3) else "",
            "length": int(table.item(row, 4).text()) if table.item(row, 4) else 0,
            "rating": float(table.item(row, 5).text()) if table.item(row, 5) else 0.0,
            "member": table.item(row, 6).text() if table.item(row, 6) else "",
            "date_added": get_current_date(),
            "read_date": "",
            "score": 0
        }
        
        # Get date_added from unselected table or read_date from selected table
        if table.columnCount() > 7:
            header_text = table.horizontalHeaderItem(7).text()
            if header_text == "Date Added" and table.item(row, 7):
                book["date_added"] = table.item(row, 7).text()
            elif header_text == "Read Date" and table.item(row, 7):
                book["read_date"] = table.item(row, 7).text()
                
        return book
    
    def _select_book(self, row):
        """Move a book from unselected to selected table with date selection"""
        book = self._extract_book_data(self.unselected_table, row)
        
        # Prompt for read date - using our updated DateSelectionDialog
        date_dialog = DateSelectionDialog(self)
        if date_dialog.exec() == QDialog.DialogCode.Accepted:
            read_date = date_dialog.get_selected_date()
            book["read_date"] = read_date
            
            # Add to selected table
            self._add_book_to_table(self.selected_table, book)
            
            # Remove from unselected table
            self.unselected_table.removeRow(row)
        
    def _deselect_book(self, row):
        """Move a book from selected to unselected table and clear read date"""
        book = self._extract_book_data(self.selected_table, row)
        
        # Clear read date
        book["read_date"] = ""
        
        # Add to unselected table
        self._add_book_to_table(self.unselected_table, book)
        
        # Remove from selected table
        self.selected_table.removeRow(row)
    
    def _update_read_date(self, row):
        """Update the read date for a selected book"""
        if not self.selected_table.item(row, 7):
            return
            
        # Get current date to pass as initial value
        current_date = self.selected_table.item(row, 7).text()
        
        # Use our custom calendar dialog with initial date
        date_dialog = DateSelectionDialog(self, current_date)
        if date_dialog.exec() == QDialog.DialogCode.Accepted:
            read_date = date_dialog.get_selected_date()
            date_item = QTableWidgetItem(read_date)
            date_item.setData(Qt.ItemDataRole.EditRole, read_date)
            self.selected_table.setItem(row, 7, date_item)
    
    def _remove_book(self, table, row):
        """Remove a book from the specified table"""
        if row < 0:
            return
            
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to remove this book?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            table.removeRow(row)
    
    def _add_book_to_table(self, table, book):
        """Add a book to the specified table"""
        row = table.rowCount()
        table.setSortingEnabled(False)
        table.insertRow(row)
        
        table.setItem(row, 0, QTableWidgetItem(book["title"]))
        table.setItem(row, 1, QTableWidgetItem(book["author"]))
        
        # ISBN
        isbn_item = BookTableItem(book.get("isbn", ""))
        if isbn_item.text():
            if cleaned_isbn := validate_isbn(isbn_item.text()):
                isbn_item.setText(cleaned_isbn)
        table.setItem(row, 2, isbn_item)
        
        # Tags
        tags = book.get("tags", "")
        tags_item = BookTableItem(tags, is_tag_column=True)
        tags_item.setData(Qt.ItemDataRole.EditRole, tags)
        table.setItem(row, 3, tags_item)
        
        # Word count
        word_count = int(book["length"]) if book["length"] else 0
        words_item = NumericTableItem(word_count)
        words_item.setData(Qt.ItemDataRole.DisplayRole, str(word_count))
        table.setItem(row, 4, words_item)
        
        # Rating
        rating = float(book["rating"]) if book["rating"] else 0.0
        rating_item = NumericTableItem(rating)
        rating_item.setData(Qt.ItemDataRole.DisplayRole, str(rating))
        table.setItem(row, 5, rating_item)
        
        # Member
        table.setItem(row, 6, QTableWidgetItem(book["member"]))
        
        # Date column (either date_added or read_date)
        if table.columnCount() > 7:
            header_text = table.horizontalHeaderItem(7).text()
            date_item = QTableWidgetItem()
            if header_text == "Date Added":
                date_item.setData(Qt.ItemDataRole.DisplayRole, book["date_added"])
                date_item.setData(Qt.ItemDataRole.EditRole, book["date_added"])
            else:
                date_item.setData(Qt.ItemDataRole.DisplayRole, book.get("read_date", ""))
                date_item.setData(Qt.ItemDataRole.EditRole, book.get("read_date", ""))
            table.setItem(row, 7, date_item)
            
        table.setSortingEnabled(True)

    def _save_changes(self):
        profile = (
            self.profile_manager.get_current_profile() if self.profile_manager else None
        )
        books = []

        # Process unselected table
        for row in range(self.unselected_table.rowCount()):
            book = self._extract_book_data(self.unselected_table, row)
            if any(book.values()):
                book["score"] = self.calculate_book_score(book)
                books.append(book)

        # Process selected table
        for row in range(self.selected_table.rowCount()):
            book = self._extract_book_data(self.selected_table, row)
            if any(book.values()):
                book["score"] = self.calculate_book_score(book)
                books.append(book)

        books = self.calculate_scores(books)
        write_db(books, profile)
        self.saved.emit()

    def _remove_selected(self):
        for table in [self.unselected_table, self.selected_table]:
            rows = sorted({item.row() for item in table.selectedItems()}, reverse=True)
            for row in rows:
                table.removeRow(row)

    def _add_row(self):
        self.unselected_table.insertRow(self.unselected_table.rowCount())
        date_col = 7  # Column index for date_added
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