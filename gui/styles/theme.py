from utils.core.paths import resource_path

# Define asset paths
UP_ARROW_PATH = resource_path("assets/up_arrow.png").replace("\\", "/")
DOWN_ARROW_PATH = resource_path("assets/down_arrow.png").replace("\\", "/")

# Base theme settings for window and widgets
BASE_THEME = """
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
    }
"""

# Button styles
BUTTON_STYLES = """
    QPushButton {
        background-color: #0d47a1;
        border: none;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #1565c0;
    }
"""

# Input field styles (LineEdit, SpinBox, etc.)
INPUT_STYLES = """
    QLineEdit, QSpinBox, QDoubleSpinBox, QTableWidget, QTableView {
        padding: 8px;
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        color: white;
        min-height: 20px;
    }
"""

# Table styles
TABLE_STYLES = """
    QTableWidget::item {
        padding: 8px;
    }
    QTableWidget QHeaderView::section {
        background-color: #2d2d2d;
        color: white;
        padding: 8px;
    }
    QTableWidget QTableCornerButton::section {
        background-color: #2d2d2d;
    }
"""

# Calendar widget styles
CALENDAR_STYLES = """
    QCalendarWidget {
        background-color: #2d2d2d;
    }
    QCalendarWidget QWidget {
        alternate-background-color: #2d2d2d;
    }
    QCalendarWidget QAbstractItemView {
        background-color: #2d2d2d;
        selection-background-color: #0d47a1;
        selection-color: white;
    }
    QCalendarWidget QAbstractItemView:enabled {
        color: white;
    }
    QCalendarWidget QAbstractItemView:disabled {
        color: #666666;
    }
    /* Month selection menu */
    QCalendarWidget QMenu {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #3d3d3d;
    }
    /* Spinbox for year selection */
    QCalendarWidget QSpinBox {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        padding: 2px;
    }
    QCalendarWidget QToolButton {
        color: white;
        background-color: transparent;
        margin: 2px;
        border-radius: 4px;
    }
    QCalendarWidget QToolButton:hover {
        background-color: #2d2d2d;
    }
    QCalendarWidget QToolButton::menu-indicator {
        image: none;
    }
    QCalendarWidget #qt_calendar_navigationbar {
        background-color: #1e1e1e;
        min-height: 40px;
    }
    QCalendarWidget #qt_calendar_prevmonth {
        qproperty-icon: url(assets/left_arrow.png);
        min-width: 24px;
    }
    QCalendarWidget #qt_calendar_nextmonth {
        qproperty-icon: url(assets/right_arrow.png);
        min-width: 24px;
    }
"""


# SpinBox specific styles
SPINBOX_STYLES = """
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        width: 20px;
        background-color: #3d3d3d;
        border: none;
        subcontrol-origin: border;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #4d4d4d;
    }
    QSpinBox::up-button,
    QDoubleSpinBox::up-button {
        subcontrol-position: top right;
    }
    QSpinBox::down-button,
    QDoubleSpinBox::down-button {
        subcontrol-position: bottom right;
    }
    QSpinBox::up-arrow,
    QDoubleSpinBox::up-arrow {
        image: url("%s");
        width: 10px;
        height: 10px;
    }
    QSpinBox::down-arrow,
    QDoubleSpinBox::down-arrow {
        image: url("%s");
        width: 10px;
        height: 10px;
    }
    QSpinBox, QDoubleSpinBox {
        padding-right: 15px;
        min-width: 75px;
    }
""" % (UP_ARROW_PATH, DOWN_ARROW_PATH)

# Custom button styles
CUSTOM_BUTTON_STYLES = """
    QPushButton#profileButton {
        background-color: transparent;
        border: none;
        width: 30px;
        height: 30px;
    }
    QPushButton#profileButton:hover {
        background-color: #2d2d2d;
    }
"""

# Store button styles
STORE_BUTTON_STYLES = """
    QPushButton#goodreads_button,
    QPushButton#amazon_button,
    QPushButton#kobo_button {
        background-color: transparent;
        border: none;
        padding: 5px;
    }
    QPushButton#goodreads_button:hover,
    QPushButton#amazon_button:hover,
    QPushButton#kobo_button:hover {
        background-color: #2d2d2d;
    }
"""

# Navigation and list styles
NAV_AND_LIST_STYLES = """
    QPushButton#nav_button {
        background-color: transparent;
        border: none;
    }
    QPushButton#nav_button:hover {
        background-color: #2d2d2d;
    }
    QPushButton#nav_button:disabled {
        background-color: transparent;
    }
    QListWidget {
        background-color: #2d2d2d;
        border: none;
        border-radius: 4px;
    }
    QListWidget::item {
        background: transparent;
    }
    QListWidget::item:hover {
        background-color: #3d3d3d;
    }
    QListWidget::item:selected {
        background-color: #444444;
        color: white;
    }
"""

# Checkbox styles
CHECKBOX_STYLES = """
    QCheckBox {
        background: transparent;
    }
    
    QCheckBox::indicator {
        width: 12px;
        height: 12px;
        border-radius: 2px;
        border: 1px solid #3d3d3d;
        background: #2d2d2d;
    }
    
    QCheckBox::indicator:hover {
        border-color: #4d4d4d;
    }
    
    QCheckBox::indicator:checked {
        background-color: #1565c0;
        image: url("assets/check.png");
    }
"""
#        

# Combine all styles into the final DARK_THEME
DARK_THEME = (
    BASE_THEME +
    BUTTON_STYLES +
    INPUT_STYLES +
    TABLE_STYLES +
    CALENDAR_STYLES +
    SPINBOX_STYLES +
    CUSTOM_BUTTON_STYLES +
    STORE_BUTTON_STYLES +
    NAV_AND_LIST_STYLES +
    CHECKBOX_STYLES
)