from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QLabel, 
                           QPushButton, QListWidget, QCalendarWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QIcon
from utils.core.dates import get_next_monday
from utils.core.paths import resource_path

def create_left_column(book_manager):
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
    weekend_format.setForeground(Qt.GlobalColor.white)

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
    
    return left_column

def create_right_column(book_manager):
    right_column = QWidget()
    layout = QVBoxLayout(right_column)
    
    # Header with navigation
    header_widget = QWidget()
    header_layout = QHBoxLayout(header_widget)
    header_layout.setContentsMargins(0, 0, 0, 0)
    
    title_label = QLabel("Selected Book")
    header_layout.addWidget(title_label)
    
    # Navigation buttons
    nav_widget = QWidget()
    nav_layout = QHBoxLayout(nav_widget)
    nav_layout.setContentsMargins(0, 0, 0, 0)
    nav_layout.setSpacing(4)
    
    # Create navigation buttons with icons
    first_button = QPushButton()
    first_button.setIcon(QIcon(resource_path("assets/first.png")))
    first_button.setToolTip("First")
    first_button.clicked.connect(book_manager.navigate_to_first)
    
    prev_button = QPushButton()
    prev_button.setIcon(QIcon(resource_path("assets/left_arrow.png")))
    prev_button.setToolTip("Previous")
    prev_button.clicked.connect(book_manager.navigate_to_prev)
    
    current_button = QPushButton()
    current_button.setIcon(QIcon(resource_path("assets/current.png")))
    current_button.setToolTip("Current")
    current_button.clicked.connect(book_manager.navigate_to_current)
    
    next_button = QPushButton()
    next_button.setIcon(QIcon(resource_path("assets/right_arrow.png")))
    next_button.setToolTip("Next")
    next_button.clicked.connect(book_manager.navigate_to_next)
    
    last_button = QPushButton()
    last_button.setIcon(QIcon(resource_path("assets/last.png")))
    last_button.setToolTip("Last")
    last_button.clicked.connect(book_manager.navigate_to_last)
    
    # Store buttons for enabling/disabling
    book_manager.nav_buttons = {
        "first": first_button,
        "prev": prev_button,
        "current": current_button,
        "next": next_button,
        "last": last_button
    }
    
    # Style the navigation buttons
    for button in book_manager.nav_buttons.values():
        button.setFixedSize(24, 24)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
            }
            QPushButton:disabled {
                background-color: transparent;
            }
        """)
    
    nav_layout.addWidget(first_button)
    nav_layout.addWidget(prev_button)
    nav_layout.addWidget(current_button)
    nav_layout.addWidget(next_button)
    nav_layout.addWidget(last_button)
    
    header_layout.addWidget(nav_widget, alignment=Qt.AlignmentFlag.AlignRight)
    layout.addWidget(header_widget)
    
    book_manager.cover_label = QLabel()
    book_manager.cover_label.setFixedSize(300, 450)
    book_manager.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    book_manager.details_label = QLabel()
    book_manager.details_label.setWordWrap(True)
    
    layout.addWidget(book_manager.cover_label)
    layout.addWidget(book_manager.details_label)
    layout.addStretch()
    
    return right_column