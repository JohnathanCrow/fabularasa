"""Module containing application styles."""
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
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #4d4d4d;
    }
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
        image: url(assets/up_arrow.png);
        width: 10px;
        height: 10px;
    }
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
        image: url(assets/down_arrow.png);
        width: 10px;
        height: 10px;
    }
    QSpinBox, QDoubleSpinBox {
        padding-right: 15px;
    }
"""