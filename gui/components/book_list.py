from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QHeaderView, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QVBoxLayout, QListWidget,
                            QWidget, QLineEdit, QInputDialog, QStyledItemDelegate)

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

    return table

def handle_cell_double_click(table, row, col):
    if col == 3:  # Tags column
        item = table.item(row, col)
        if item:
            dialog = TagEditorDialog(item.get_tags_string(), table)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_tags = dialog.get_tags_string()
                item.setData(Qt.ItemDataRole.EditRole, new_tags)

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

        words_item = QTableWidgetItem()
        words_item.setData(Qt.ItemDataRole.DisplayRole, str(book["length"]))
        words_item.setData(Qt.ItemDataRole.EditRole, int(book["length"]))
        table.setItem(row, 4, words_item)

        rating_item = QTableWidgetItem()
        rating_item.setData(Qt.ItemDataRole.DisplayRole, str(book["rating"]))
        rating_item.setData(Qt.ItemDataRole.EditRole, float(book["rating"]))
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
        self.unselected_table.sortItems(7, Qt.SortOrder.DescendingOrder)
        self.selected_table.sortItems(7, Qt.SortOrder.DescendingOrder)

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
                "tags": (
                    self.unselected_table.item(row, 3).get_tags_string()
                    if self.unselected_table.item(row, 3)
                    else ""
                ),
                "length": (
                    int(self.unselected_table.item(row, 4).text())
                    if self.unselected_table.item(row, 4)
                    else 0
                ),
                "rating": (
                    float(self.unselected_table.item(row, 5).text())
                    if self.unselected_table.item(row, 5)
                    else 0.0
                ),
                "member": (
                    self.unselected_table.item(row, 6).text()
                    if self.unselected_table.item(row, 6)
                    else ""
                ),
                "date_added": (
                    self.unselected_table.item(row, 7).text()
                    if self.unselected_table.item(row, 7)
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
                "tags": (
                    self.selected_table.item(row, 3).get_tags_string()
                    if self.selected_table.item(row, 3)
                    else ""
                ),
                "length": (
                    int(self.selected_table.item(row, 4).text())
                    if self.selected_table.item(row, 4)
                    else 0
                ),
                "rating": (
                    float(self.selected_table.item(row, 5).text())
                    if self.selected_table.item(row, 5)
                    else 0.0
                ),
                "member": (
                    self.selected_table.item(row, 6).text()
                    if self.selected_table.item(row, 6)
                    else ""
                ),
                "date_added": get_current_date(),
                "read_date": (
                    self.selected_table.item(row, 7).text()
                    if self.selected_table.item(row, 7)
                    else ""
                ),
                "score": 0,
            }
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
