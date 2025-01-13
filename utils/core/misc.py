import json

from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QVBoxLayout)

from .paths import (get_data_dir, get_profiles, get_state_file_path,
                    resource_path)


class MiscSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Load settings
        self.settings_path = get_state_file_path("misc_settings.json")
        self.settings = self.load_settings()

        layout = QVBoxLayout(self)

        # Amazon settings
        amazon_layout = QVBoxLayout()
        amazon_layout.addWidget(QLabel("Amazon Region"))
        self.amazon_input = QLineEdit(self.settings.get("amazon_address", ".com"))
        amazon_layout.addWidget(self.amazon_input)
        layout.addLayout(amazon_layout)

        # Kobo settings
        kobo_layout = QVBoxLayout()
        kobo_layout.addWidget(QLabel("Kobo Region"))
        self.kobo_input = QLineEdit(self.settings.get("kobo_region", "us/en"))
        kobo_layout.addWidget(self.kobo_input)
        layout.addLayout(kobo_layout)

        layout.addStretch()

        # Help text
        help_text = QLabel(
            """
Examples:
Amazon: .co.uk, .de, .fr, .jp
Kobo: gb/en, de/de, fr/fr, jp/ja"""
        )
        help_text.setStyleSheet("color: #888;")
        layout.addWidget(help_text)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.resize(400, 400)

    def load_settings(self):
        try:
            with open(get_state_file_path("misc_settings.json"), "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"amazon_address": ".com", "kobo_region": "us/en"}

    def save_settings(self):
        amazon_address = self.amazon_input.text().strip()
        kobo_region = self.kobo_input.text().strip()

        # Use default values if the fields are empty
        if not amazon_address:
            amazon_address = ".com"
        if not kobo_region:
            kobo_region = "us/en"

        settings = {
            "amazon_address": amazon_address,
            "kobo_region": kobo_region,
        }

        try:
            with open(self.settings_path, "w") as f:
                json.dump(settings, f)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

