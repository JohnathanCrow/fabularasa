import json
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QListWidget, QInputDialog, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from .paths import get_data_dir, get_profiles
from .config import DEFAULT_CONFIG, save_config

class ProfileManagementDialog(QDialog):
    def __init__(self, parent=None, profile_manager=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.current_profile = profile_manager.get_current_profile()
        
        self.setWindowTitle("Manage Profiles")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        current_profile_label = QLabel(f"Current Profile: {self.current_profile}")
        current_profile_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(current_profile_label)
        
        self.profile_list = QListWidget()
        self.profile_list.itemDoubleClicked.connect(self.switch_to_profile)
        self.refresh_profile_list()
        layout.addWidget(self.profile_list)
        
        button_layout = QHBoxLayout()
        
        self.new_button = QPushButton("Create")
        self.new_button.clicked.connect(self.create_new_profile)
        
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
        current_text = current_item.text() if current_item else None
        
        self.profile_list.clear()
        for profile in self.profile_manager.get_available_profiles():
            self.profile_list.addItem(profile)
            
        if current_text:
            items = self.profile_list.findItems(current_text, Qt.MatchFlag.MatchExactly)
            if items:
                self.profile_list.setCurrentItem(items[0])

    def switch_to_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        profile_name = current_item.text()
        if profile_name == self.current_profile:
            QMessageBox.information(self, "Info", f"Already using profile '{profile_name}'")
            return
            
        self.profile_manager.set_current_profile(profile_name)
        self.current_profile = profile_name
        
        parent = self.parent()
        parent.setWindowTitle(f"Fabula Rasa - {profile_name}")
        parent.book_manager.reload_data()
        
        if parent.config_widget:
            parent.config_widget.load_values()
        
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text().startswith("Current Profile:"):
                widget.setText(f"Current Profile: {profile_name}")
                break

    def update_button_states(self):
        selected = self.profile_list.currentItem() is not None
        is_default = selected and self.profile_list.currentItem().text() == 'default'
        is_current = selected and self.profile_list.currentItem().text() == self.current_profile
        
        self.rename_button.setEnabled(selected and not is_default)
        self.delete_button.setEnabled(selected and not is_default)
        self.switch_button.setEnabled(selected and not is_current)

    def create_new_profile(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("New Profile")
        dialog.setLabelText("Profile Name:")
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            profile_name = dialog.textValue().strip()
            if not profile_name:
                QMessageBox.warning(self, "Error", "Profile name cannot be empty")
                return
                
            if profile_name in self.profile_manager.get_available_profiles():
                QMessageBox.warning(self, "Error", "Profile already exists")
                return
                
            if self.profile_manager.create_profile(profile_name):
                self.refresh_profile_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to create profile")

    def rename_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        old_name = current_item.text()
        if old_name == 'default':
            QMessageBox.warning(self, "Error", "Cannot rename default profile")
            return
            
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Rename Profile")
        dialog.setLabelText("Profile Name:")
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.setTextValue(old_name)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.textValue().strip()
            if not new_name:
                QMessageBox.warning(self, "Error", "Profile name cannot be empty")
                return
                
            if new_name in self.profile_manager.get_available_profiles():
                QMessageBox.warning(self, "Error", "Profile name already exists")
                return
                
            try:
                old_path = Path(self.profile_manager._get_profile_dir(old_name))
                new_path = Path(self.profile_manager._get_profile_dir(new_name))
                
                shutil.move(str(old_path), str(new_path))
                
                if self.profile_manager.get_current_profile() == old_name:
                    self.profile_manager.set_current_profile(new_name)
                    self.parent().setWindowTitle(f"Fabula Rasa - {new_name}")
                
                self.refresh_profile_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to rename profile: {str(e)}")

    def delete_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        profile_name = current_item.text()
        if profile_name == 'default':
            QMessageBox.warning(self, "Error", "Cannot delete default profile")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete profile '{profile_name}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.profile_manager.get_current_profile() == profile_name:
                    self.profile_manager.set_current_profile('default')
                    self.parent().setWindowTitle("Fabula Rasa - default")
                    self.parent().book_manager.reload_data()
                
                profile_dir = Path(self.profile_manager._get_profile_dir(profile_name))
                shutil.rmtree(str(profile_dir))
                
                self.refresh_profile_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete profile: {str(e)}")

class ProfileManager:
    def __init__(self):
        self.current_profile = 'default'
        self._load_last_profile()
    
    def _get_profile_state_path(self):
        return Path(get_data_dir()) / 'profile_state.json'
    
    def _load_last_profile(self):
        try:
            with open(self._get_profile_state_path(), 'r') as f:
                state = json.load(f)
                self.current_profile = state.get('last_profile', 'default')
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_profile = 'default'
    
    def _save_profile_state(self):
        with open(self._get_profile_state_path(), 'w') as f:
            json.dump({'last_profile': self.current_profile}, f)
    
    def get_current_profile(self) -> str:
        return self.current_profile
    
    def set_current_profile(self, profile_name: str):
        self.current_profile = profile_name
        self._save_profile_state()
    
    def _get_profile_dir(self, profile_name: str) -> str:
        return str(Path(get_data_dir(profile_name)))
    
    def create_profile(self, profile_name: str) -> bool:
        if not profile_name or profile_name in get_profiles():
            return False
        
        try:
            profile_dir = Path(get_data_dir(profile_name))
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            db_path = profile_dir / "books.db"
            if not db_path.exists():
                db_path.touch()
            
            save_config(DEFAULT_CONFIG, profile_name)
            
            return True
        except Exception as e:
            print(f"Error creating profile: {e}")
            return False
    
    def get_available_profiles(self) -> list:
        return get_profiles()
    
    def show_management_dialog(self, parent=None):
        dialog = ProfileManagementDialog(parent, self)
        dialog.exec()