"""Module for the main application interface."""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                           QListWidget, QTabWidget, QCalendarWidget)
from PyQt6.QtGui import (QIcon, QFontDatabase, QFont, QTextCharFormat)
from PyQt6.QtCore import Qt
from .book_table import BookListWidget
from .styles import DARK_THEME
from .book_manager import BookManager
from utils.db import read_csv_file
from utils.dates import get_next_monday
from .config_tab import ConfigWidget

class BookClubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fabula Rasa")
        self.setStyleSheet(DARK_THEME)
        self.setMinimumSize(910, 810)
        

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        icon_path = os.path.join(parent_dir, "assets", "icon.png")
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")

        self.book_manager = BookManager(self)
        self.setCentralWidget(create_main_layout(self.book_manager, self))
        self.book_manager.update_current_selection()

def create_main_layout(book_manager, window):
    """Create the main application layout."""
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    
    # Load the custom font
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "CinzelDecorative.ttf")
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            print(f"Failed to load font: {font_path}")
            font_family = "Default Font"  # Fallback
    else:
        print(f"Font file not found: {font_path}")
        font_family = "Default Font"  # Fallback

    header = QLabel("Fabula Rasa")
    header.setStyleSheet(f"font-size: 30px; font-weight: bold; margin: 10px; font-family: '{font_family}';")
    header.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(header)
    
    tabs = QTabWidget()
    tabs.addTab(create_selection_layout(book_manager), "Home")
    
    book_list = BookListWidget()
    book_list.load_books(read_csv_file("books.csv"))
    tabs.addTab(book_list, "Database")
    
    tabs.addTab(ConfigWidget(window), "Config")
    
    book_manager.book_list_widget = book_list
    
    layout.addWidget(tabs)
    return main_widget

def create_selection_layout(book_manager):
    """Create the book selection tab layout."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    
    layout.addWidget(create_left_column(book_manager))
    layout.addWidget(create_right_column(book_manager))
    
    return widget

def create_left_column(book_manager):
    """Create the left column of the selection tab."""
    from PyQt6.QtGui import QTextCharFormat
    from PyQt6.QtCore import Qt

    left_column = QWidget()
    layout = QVBoxLayout(left_column)
    
    # Book input fields
    book_manager.book_input = QLineEdit()
    book_manager.book_input.setPlaceholderText("Enter title or ISBN...")
    book_manager.author_input = QLineEdit()
    book_manager.author_input.setPlaceholderText("Enter author...")
    book_manager.word_count_input = QLineEdit()
    book_manager.word_count_input.setPlaceholderText("Enter word count...")
    book_manager.member_input = QLineEdit()
    book_manager.member_input.setPlaceholderText("Enter member...")
    
    book_manager.book_input.returnPressed.connect(
        lambda: book_manager.author_input.setFocus()
    )
    book_manager.author_input.returnPressed.connect(
        lambda: book_manager.word_count_input.setFocus()
    )
    book_manager.word_count_input.returnPressed.connect(
        lambda: book_manager.member_input.setFocus()
    )
    book_manager.member_input.returnPressed.connect(book_manager.add_book)
    
    # Buttons
    add_button = QPushButton("Add")
    add_button.clicked.connect(book_manager.add_book)
    
    select_button = QPushButton("Select")
    select_button.clicked.connect(book_manager.select_book)
    
    book_manager.selected_list = QListWidget()
    book_manager.update_selected_list()
    
    # Calendar settings
    read_date_label = QLabel("Next Book")
    weekend_format = QTextCharFormat()
    weekend_format.setForeground(Qt.GlobalColor.white)  # Change weekend color to white

    book_manager.read_date_calendar = QCalendarWidget()
    book_manager.read_date_calendar.setSelectedDate(get_next_monday())
    book_manager.read_date_calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
    
    # Apply custom format to weekends
    for day in [Qt.DayOfWeek.Saturday, Qt.DayOfWeek.Sunday]:
        book_manager.read_date_calendar.setWeekdayTextFormat(day, weekend_format)
    
    # Add widgets to layout
    layout.addWidget(QLabel("New Book"))
    layout.addWidget(book_manager.book_input)
    layout.addWidget(book_manager.author_input)
    layout.addWidget(book_manager.word_count_input)
    layout.addWidget(book_manager.member_input)
    layout.addWidget(add_button)
    layout.addWidget(read_date_label)
    layout.addWidget(book_manager.read_date_calendar)
    layout.addWidget(select_button)
    # layout.addWidget(QLabel("Previous Books"))
    # layout.addWidget(book_manager.selected_list)
    
    return left_column


def create_right_column(book_manager):
    """Create the right column of the selection tab."""
    right_column = QWidget()
    layout = QVBoxLayout(right_column)
    
    book_manager.cover_label = QLabel()
    book_manager.cover_label.setFixedSize(300, 450)
    book_manager.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    book_manager.details_label = QLabel()
    book_manager.details_label.setWordWrap(True)
    
    layout.addWidget(QLabel("Selected Book"))
    layout.addWidget(book_manager.cover_label)
    layout.addWidget(book_manager.details_label)
    layout.addStretch()
    
    return right_column

def main():
    """Start the application."""
    app = QApplication(sys.argv)
    window = BookClubWindow()
    window.show()
    sys.exit(app.exec())