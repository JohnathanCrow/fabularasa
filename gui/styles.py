"""Module containing application styles."""
from utils.paths import resource_path
import os

# Use absolute paths for the arrow images
UP_ARROW_PATH = resource_path("assets/up_arrow.png").replace("\\", "/")
DOWN_ARROW_PATH = resource_path("assets/down_arrow.png").replace("\\", "/")

DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    QPushButton {
        background-color: #0d47a1;
        border: none;
        padding: 8px;
        border-radius: 4px;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #1565c0;
    }
    QLineEdit, QSpinBox, QDoubleSpinBox, QTableWidget, QTableView {
        padding: 8px;
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        color: white;
        min-height: 20px;
    }
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
    QListWidget {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
    }
    QLabel {
        color: #ffffff;
    }
    
    /* Calendar Styling */
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
    
    QCalendarWidget QMenu {
        background-color: #2d2d2d;
    }
    
    QCalendarWidget QSpinBox {
        background-color: #2d2d2d;
        color: white;
    }
    
    QCalendarWidget QToolButton {
        color: white;
        background-color: transparent;
        margin: 2px;
        border-radius: 4px;
    }
    
    QCalendarWidget QToolButton:hover {
        background-color: #0d47a1;
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

    /* Original SpinBox styling */
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