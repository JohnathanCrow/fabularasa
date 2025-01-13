import csv
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QDialog, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from utils.common.constants import DATE_FORMAT, DB_FILE

from .db import read_db
from .paths import (get_data_dir, get_profiles, get_state_file_path,
                    resource_path)


class ProfileListItem(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Set explicit background for the widget
        self.setStyleSheet("background: transparent;")

        self.label = QLabel(text)
        self.label.setStyleSheet("background: transparent;")

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(False)
        self.checkbox.setStyleSheet("background: transparent;")

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.checkbox)


def refresh_profile_list(self):
    self.profile_list.clear()
    for profile in get_profiles():
        item = QListWidgetItem(self.profile_list)
        widget = ProfileListItem(profile)
        # Set the item's background to transparent
        item.setBackground(Qt.GlobalColor.transparent)
        item.setSizeHint(widget.sizeHint())
        self.profile_list.addItem(item)
        self.profile_list.setItemWidget(item, widget)


class ExportManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Load last used export directory
        self.settings_path = Path(get_state_file_path("export_settings.json"))
        self.export_dir = self.load_export_directory()

        layout = QVBoxLayout(self)

        # Export directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Directory:"))
        self.dir_edit = QLineEdit(self.export_dir)
        self.dir_edit.textChanged.connect(self.save_export_directory)
        dir_layout.addWidget(self.dir_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)

        # Profile list with checkboxes
        self.profile_list = QListWidget()
        self.refresh_profile_list()
        layout.addWidget(self.profile_list)
        # Export buttons
        button_layout = QHBoxLayout()

        csv_btn = QPushButton("CSV")
        csv_btn.clicked.connect(self.export_csv)

        md_btn = QPushButton("MD")
        md_btn.clicked.connect(self.export_markdown)

        backup_btn = QPushButton("Backup")
        backup_btn.clicked.connect(self.backup_profiles)

        restore_btn = QPushButton("Restore")
        restore_btn.clicked.connect(self.restore_profiles)

        button_layout.addWidget(csv_btn)
        button_layout.addWidget(md_btn)
        button_layout.addWidget(backup_btn)
        button_layout.addWidget(restore_btn)

        layout.addLayout(button_layout)

        self.resize(400, 400)

    def load_export_directory(self) -> str:
        try:
            with open(self.settings_path, "r") as f:
                settings = json.load(f)
                return settings.get("export_dir", str(Path.home() / "Documents"))
        except (FileNotFoundError, json.JSONDecodeError):
            return str(Path.home() / "Documents")

    def save_export_directory(self):
        try:
            with open(self.settings_path, "w") as f:
                json.dump({"export_dir": self.dir_edit.text()}, f)
        except Exception as e:
            print(f"Error saving export directory: {e}")

    def browse_directory(self):
        if directory := QFileDialog.getExistingDirectory(
            self, "Select Directory", self.dir_edit.text()
        ):
            self.dir_edit.setText(directory)

    def refresh_profile_list(self):
        self.profile_list.clear()
        for profile in get_profiles():
            item = QListWidgetItem(self.profile_list)
            widget = ProfileListItem(profile)
            item.setSizeHint(widget.sizeHint())
            self.profile_list.addItem(item)
            self.profile_list.setItemWidget(item, widget)

    def get_selected_profiles(self) -> List[str]:
        selected = []
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            widget = self.profile_list.itemWidget(item)
            if widget.checkbox.isChecked():
                selected.append(widget.label.text())
        return selected

    def export_csv(self):
        selected_profiles = self.get_selected_profiles()
        if not selected_profiles:
            QMessageBox.warning(self, "Error", "No profiles selected")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path(self.dir_edit.text())

        try:
            for profile in selected_profiles:
                books = read_db(profile)  # Modified: removed DB_FILE argument
                if not books:
                    continue

                filename = export_dir / f"{profile}_books_{timestamp}.csv"
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=books[0].keys())
                    writer.writeheader()
                    writer.writerows(books)

            QMessageBox.information(self, "Success", "CSV export completed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def export_markdown(self):
        selected_profiles = self.get_selected_profiles()
        if not selected_profiles:
            QMessageBox.warning(self, "Error", "No profiles selected")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path(self.dir_edit.text())

        try:
            for profile in selected_profiles:
                books = read_db(profile)  # Modified: removed DB_FILE argument
                if not books:
                    continue

                # Filter read books and sort by date
                read_books = [b for b in books if b.get("read_date")]
                read_books.sort(key=lambda x: x["read_date"])

                filename = export_dir / f"{profile}_books_{timestamp}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    for book in read_books:
                        read_date = datetime.strptime(book["read_date"], DATE_FORMAT)
                        formatted_date = read_date.strftime("%d/%m/%Y")

                        f.write(f"### {book['title']}, _{book['author']}_\n\n")
                        f.write(f"**ISBN:** {book.get('isbn', 'N/A')}\n")
                        f.write(f"**Words:** {book['length']}\n")
                        f.write(f"**Rating:** {book['rating']}\n\n")
                        f.write(f"**Member:** {book['member']}\n")
                        f.write(f"**Read:** {formatted_date}\n\n")
                        f.write("---\n\n")

            QMessageBox.information(self, "Success", "Markdown export completed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def backup_profiles(self):
        selected_profiles = self.get_selected_profiles()
        if not selected_profiles:
            QMessageBox.warning(self, "Error", "No profiles selected")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path(self.dir_edit.text())
        zip_path = export_dir / f"FabulaRasa-{timestamp}.zip"

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for profile in selected_profiles:
                    profile_dir = Path(get_data_dir(profile))

                    db_path = profile_dir / DB_FILE
                    if db_path.exists():
                        zipf.write(db_path, f"{profile}/books.db")

                    config_path = profile_dir / "config.json"
                    if config_path.exists():
                        zipf.write(config_path, f"{profile}/config.json")

            QMessageBox.information(self, "Success", "Backup completed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {str(e)}")

    def restore_profiles(self):
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", self.dir_edit.text(), "Zip files (*.zip)"
        )

        if not zip_path:
            return

        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                # Validate zip structure
                files = zipf.namelist()
                profiles = {f.split("/")[0] for f in files}

                if existing := [p for p in profiles if Path(get_data_dir(p)).exists()]:
                    msg = "The following profiles will be overwritten:\n\n" + "\n".join(
                        existing
                    )
                    msg += "\n\nDo you want to continue?"

                    reply = QMessageBox.question(
                        self,
                        "Confirm Restore",
                        msg,
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    )

                    if reply == QMessageBox.StandardButton.No:
                        return

                # Extract files
                for profile in profiles:
                    profile_dir = Path(get_data_dir(profile))
                    profile_dir.mkdir(parents=True, exist_ok=True)

                    # Extract only .db and .json files
                    for file in files:
                        if file.startswith(f"{profile}/") and file.endswith(
                            (".db", ".json")
                        ):
                            zipf.extract(file, profile_dir.parent)

                # Switch to default profile if it exists in the restored profiles
                if "default" in profiles:
                    parent = self.parent()
                    if parent and hasattr(parent, "profile_manager"):
                        parent.profile_manager.set_current_profile("default")
                        parent.setWindowTitle("Fabula Rasa - default")
                        parent.book_manager.reload_data()
                        if parent.config_widget:
                            parent.config_widget.reload_profile()

                QMessageBox.information(self, "Success", "Restore completed")
                self.refresh_profile_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Restore failed: {str(e)}")
