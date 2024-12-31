"""Module containing application styles."""
from utils.paths import resource_path
import os

# Use absolute paths for the arrow images
UP_ARROW_PATH = resource_path("assets/up_arrow.png").replace("\\", "/")
DOWN_ARROW_PATH = resource_path("assets/down_arrow.png").replace("\\", "/")

#print(f"Current working directory: {os.getcwd()}")
#print(f"Up arrow path: {UP_ARROW_PATH}")
#print(f"Down arrow path: {DOWN_ARROW_PATH}")
#print(f"Files exist?")
#print(f"Up arrow exists: {os.path.exists(UP_ARROW_PATH)}")
#print(f"Down arrow exists: {os.path.exists(DOWN_ARROW_PATH)}")

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
    QDoubleSpinBox::up-arrow {{
        image: url("{UP_ARROW_PATH}");
        width: 10px;
        height: 10px;
    }}

    QSpinBox::down-arrow,
    QDoubleSpinBox::down-arrow {{
        image: url("{DOWN_ARROW_PATH}");
        width: 10px;
        height: 10px;
    }}

    QSpinBox, QDoubleSpinBox {
        padding-right: 15px;
        min-width: 75px;
    }
"""