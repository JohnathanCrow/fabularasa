import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from utils.core.export import ExportManagementDialog
from utils.core.misc import MiscSettingsDialog
from utils.core.paths import resource_path
from utils.core.profile import ProfileManager

from ..components.book_manager import BookManager
from ..layouts.main_layout import create_main_layout
from ..styles.theme import DARK_THEME


class BookClubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.config_widget = None
        self.setWindowTitle(
            f"Fabula Rasa - {self.profile_manager.get_current_profile()}"
        )
        self.setStyleSheet(DARK_THEME)
        self.setMinimumSize(930, 850)

        icon_path = resource_path("assets/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Profile management button
        self.profile_button = QPushButton()
        self.profile_button.setObjectName("profileButton")
        self.profile_button.setIcon(QIcon(resource_path("assets/user.png")))
        self.profile_button.setFixedSize(30, 30)
        self.profile_button.setToolTip("Profiles")
        self.profile_button.clicked.connect(self.show_profile_menu)
        header_layout.addWidget(
            self.profile_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Export management button
        self.export_button = QPushButton()
        self.export_button.setObjectName("profileButton")  # Reuse the same style
        self.export_button.setIcon(QIcon(resource_path("assets/data.png")))
        self.export_button.setFixedSize(30, 30)
        self.export_button.setToolTip("Data")
        self.export_button.clicked.connect(self.show_export_menu)
        header_layout.addWidget(
            self.export_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # misc management button
        self.misc_button = QPushButton()
        self.misc_button.setObjectName("profileButton")  # Reuse the same style
        self.misc_button.setIcon(QIcon(resource_path("assets/misc.png")))
        self.misc_button.setFixedSize(30, 30)
        self.misc_button.setToolTip("Settings")
        self.misc_button.clicked.connect(self.show_misc_menu)
        header_layout.addWidget(self.misc_button, alignment=Qt.AlignmentFlag.AlignLeft)

        font_path = resource_path("assets/CinzelDecorative.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            else:
                print(f"Failed to load font: {font_path}")
                font_family = "Default Font"
        else:
            print(f"Font file not found: {font_path}")
            font_family = "Default Font"

        header_layout.addStretch()

        header = QLabel("Fabula Rasa")
        header.setStyleSheet(
            f"font-size: 30px; font-weight: bold; padding-right: 60px; margin: 0px; font-family: '{font_family}';"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header)

        header_layout.addStretch()

        main_layout.addWidget(header_widget)

        self.book_manager = BookManager(self)
        main_layout.addWidget(create_main_layout(self.book_manager, self, font_family))

        self.setCentralWidget(main_widget)

        # Initialize book data
        self.book_manager.load_selected_books()
        self.book_manager.update_current_selection()

    def show_profile_menu(self):
        self.profile_manager.show_management_dialog(self)

    def show_misc_menu(self):
        dialog = MiscSettingsDialog(self)
        dialog.exec()

    def show_export_menu(self):
        dialog = ExportManagementDialog(self)
        dialog.exec()

    def switch_profile(self, profile_name):
        self.profile_manager.set_current_profile(profile_name)
        self.setWindowTitle(f"Fabula Rasa - {profile_name}")
        self.book_manager.reload_data()
        if self.config_widget:
            self.config_widget.reload_profile()
