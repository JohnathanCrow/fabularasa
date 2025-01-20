import json
import shutil
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QInputDialog, QLabel,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)

from utils.common.constants import DB_FILE

from .config import DEFAULT_CONFIG, save_config
from .paths import (get_data_dir, get_profiles, get_profiles_dir,
                    get_state_file_path)


class ProfileManagementDialog(QDialog):
    def __init__(self, parent=None, profile_manager=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.current_profile = profile_manager.get_current_profile()

        self.setWindowTitle("Profiles")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        self.current_profile_label = QLabel(f"Current Profile: {self.current_profile}")
        self.current_profile_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.current_profile_label)

        self.profile_list = QListWidget()
        self.profile_list.itemDoubleClicked.connect(self.switch_to_profile)
        self.refresh_profile_list()
        layout.addWidget(self.profile_list)

        button_layout = QHBoxLayout()

        self.new_button = QPushButton("Create")
        self.new_button.clicked.connect(self.create_profile)

        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_profile)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_profile)

        self.switch_button = QPushButton("Switch")
        self.switch_button.clicked.connect(self.switch_to_profile)

        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.switch_button)

        layout.addLayout(button_layout)

        self.profile_list.itemSelectionChanged.connect(self.update_button_states)
        self.update_button_states()

        self.resize(400, 400)

    def refresh_profile_list(self):
        current_item = self.profile_list.currentItem()
        current_text = (
            current_item.data(Qt.ItemDataRole.UserRole) if current_item else None
        )

        self.profile_list.clear()
        for profile in self.profile_manager.get_available_profiles():
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, profile)

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(8, 8, 8, 8)

            label = QLabel(profile)
            label.setStyleSheet("background: transparent;")

            layout.addWidget(label)
            layout.addStretch()

            widget.setStyleSheet("background: transparent;")
            item.setSizeHint(widget.sizeHint())

            self.profile_list.addItem(item)
            self.profile_list.setItemWidget(item, widget)

        if current_text:
            for index in range(self.profile_list.count()):
                if (
                    self.profile_list.item(index).data(Qt.ItemDataRole.UserRole)
                    == current_text
                ):
                    self.profile_list.setCurrentItem(self.profile_list.item(index))
                    break

    def switch_to_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "No profile selected.")
            return

        profile_name = current_item.data(Qt.ItemDataRole.UserRole)
        if not profile_name:
            QMessageBox.warning(self, "Error", "Invalid profile selection.")
            return

        if profile_name == self.current_profile:
            QMessageBox.information(
                self, "Info", f"Already using profile '{profile_name}'."
            )
            return

        try:
            self.profile_manager.set_current_profile(profile_name)
            self.current_profile = profile_name

            if parent := self.parent():
                parent.setWindowTitle(f"Fabula Rasa - {profile_name}")
                parent.book_manager.reload_data()

                if parent.config_widget:
                    parent.config_widget.load_values()

            self.current_profile_label.setText(f"Current Profile: {profile_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to switch profile: {str(e)}")

    def update_button_states(self):
        selected = self.profile_list.currentItem() is not None
        is_default = selected and self.profile_list.currentItem().text() == "default"
        is_current = (
            selected and self.profile_list.currentItem().text() == self.current_profile
        )

        self.rename_button.setEnabled(selected and not is_default)
        self.delete_button.setEnabled(selected and not is_default)
        self.switch_button.setEnabled(selected and not is_current)

    def create_profile(self):
        dialog = self.dialog_title("Create")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            profile_name = dialog.textValue().strip()

            if not profile_name:
                QMessageBox.warning(self, "Error", "Profile name cannot be empty")
                return

            if profile_name == "default":
                QMessageBox.warning(
                    self, "Error", "Cannot create a profile with the name 'default'"
                )
                return

            if profile_name in self.profile_manager.get_available_profiles():
                QMessageBox.warning(self, "Error", "Profile already exists")
                return

            if self.profile_manager.create_profile(profile_name):
                print(f"Profile '{profile_name}' created successfully!")
                self.refresh_profile_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to create profile")

    def rename_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            return

        old_name = current_item.data(Qt.ItemDataRole.UserRole)

        # Prevent renaming the default profile
        if old_name.lower() == "default":
            QMessageBox.warning(self, "Error", "Cannot rename the default profile")
            return

        dialog = self.dialog_title("Rename")
        dialog.setTextValue(old_name)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.textValue().strip()

            if not new_name:
                QMessageBox.warning(self, "Error", "Profile name cannot be empty")
                return

            if new_name.lower() == "default":
                QMessageBox.warning(self, "Error", "Cannot rename to 'default'")
                return

            # Case-insensitive check for existing profiles
            if new_name.lower() in [p.lower() for p in self.profile_manager.get_available_profiles() 
                                  if p.lower() != old_name.lower()]:
                QMessageBox.warning(self, "Error", "Profile name already exists")
                return

            try:
                old_path = Path(self.profile_manager._get_profile_dir(old_name))
                new_path = Path(self.profile_manager._get_profile_dir(new_name))

                # Find the actual case-sensitive path that exists
                actual_old_path = None
                parent_dir = old_path.parent
                if parent_dir.exists():
                    for existing_path in parent_dir.iterdir():
                        if existing_path.name.lower() == old_name.lower():
                            actual_old_path = existing_path
                            break

                if not actual_old_path:
                    QMessageBox.warning(
                        self, "Error", f"Profile folder {old_path} does not exist."
                    )
                    return

                # For Windows case-only changes, use a temporary name first
                if old_name.lower() == new_name.lower():
                    temp_path = old_path.parent / f"{old_name}_temp"
                    actual_old_path.rename(temp_path)
                    temp_path.rename(new_path)
                else:
                    # Regular rename for different names
                    actual_old_path.rename(new_path)

                # Update the profile manager if necessary
                if self.profile_manager.get_current_profile().lower() == old_name.lower():
                    self.profile_manager.set_current_profile(new_name)
                    self.parent().setWindowTitle(f"Fabula Rasa - {new_name}")

                # Refresh profile list and select the new profile
                self.refresh_profile_list()

                # Select the newly renamed profile
                for index in range(self.profile_list.count()):
                    if (self.profile_list.item(index).data(Qt.ItemDataRole.UserRole).lower() 
                        == new_name.lower()):
                        self.profile_list.setCurrentItem(self.profile_list.item(index))
                        break

            except Exception as e:
                print(f"Error during renaming: {e}")
                QMessageBox.warning(
                    self, "Error", f"Failed to rename profile: {str(e)}"
                )

    def dialog_title(self, arg0):
        result = QInputDialog(self)
        result.setWindowTitle(arg0)
        result.setLabelText("Profile Name:")
        result.setInputMode(QInputDialog.InputMode.TextInput)
        return result

    def delete_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            return

        profile_name = current_item.data(Qt.ItemDataRole.UserRole)

        if profile_name == "default":
            QMessageBox.warning(self, "Error", "Cannot delete the default profile.")
            return

        reply = QMessageBox.question(
            self,
            "Delete",
            f"Are you sure you want to delete profile '{profile_name}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.profile_manager.get_current_profile() == profile_name:
                    self.profile_manager.set_current_profile("default")
                    self.parent().setWindowTitle("Fabula Rasa - default")
                    self.parent().book_manager.reload_data()

                profile_dir = Path(self.profile_manager._get_profile_dir(profile_name))
                if profile_dir.exists():
                    shutil.rmtree(profile_dir)

                self.refresh_profile_list()
                QMessageBox.information(
                    self, "Success", f"Profile '{profile_name}' has been deleted."
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to delete profile: {str(e)}"
                )


class ProfileManager:
    def __init__(self):
        self.current_profile = "default"
        self._load_last_profile()

    def _get_profile_state_path(self):
        return Path(get_state_file_path("profile_state.json"))

    def _load_last_profile(self):
        try:
            with open(self._get_profile_state_path(), "r") as f:
                state = json.load(f)
                self.current_profile = state.get("last_profile", "default")
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_profile = "default"

    def _save_profile_state(self):
        with open(self._get_profile_state_path(), "w") as f:
            json.dump({"last_profile": self.current_profile}, f)

    def get_current_profile(self) -> str:
        return self.current_profile

    def set_current_profile(self, profile_name: str):
        self.current_profile = profile_name
        self._save_profile_state()

    def _get_profile_dir(self, profile_name: str) -> str:
        return str(get_profiles_dir() / profile_name)

    def create_profile(self, profile_name: str) -> bool:
        if not profile_name or profile_name in get_profiles():
            return False

        try:
            return self.create_profile_dir_files(profile_name)
        except Exception as e:
            print(f"Error creating profile: {e}")
            return False

    def create_profile_dir_files(self, profile_name):
        profile_dir = Path(get_data_dir(profile_name))
        profile_dir.mkdir(parents=True, exist_ok=True)

        db_path = profile_dir / DB_FILE
        if not db_path.exists():
            db_path.touch()

        save_config(DEFAULT_CONFIG, profile_name)

        return True

    def get_available_profiles(self) -> list:
        return get_profiles()

    def show_management_dialog(self, parent=None):
        dialog = ProfileManagementDialog(parent, self)
        dialog.exec()
