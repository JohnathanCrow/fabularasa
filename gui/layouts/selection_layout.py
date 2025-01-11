from PyQt6.QtWidgets import QWidget, QHBoxLayout
from .column_layouts import create_left_column, create_right_column

def create_selection_layout(book_manager):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    
    layout.addWidget(create_left_column(book_manager))
    layout.addWidget(create_right_column(book_manager))
    
    return widget