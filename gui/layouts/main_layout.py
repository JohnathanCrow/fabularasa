from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from utils.core.db import read_db
from ..components.book_list import BookListWidget
from ..components.config_widget import ConfigWidget
from .selection_layout import create_selection_layout

def create_main_layout(book_manager, window, font_family):
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    
    tabs = QTabWidget()
    tabs.addTab(create_selection_layout(book_manager), "Home")
    
    book_list = BookListWidget(profile_manager=window.profile_manager)
    book_list.load_books(read_db("books.db", window.profile_manager.get_current_profile()))
    tabs.addTab(book_list, "Database")
    
    window.config_widget = ConfigWidget(window)
    tabs.addTab(window.config_widget, "Config")
    
    book_manager.book_list_widget = book_list
    
    layout.addWidget(tabs)
    return main_widget