"""Module for the configuration interface."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSpinBox, QDoubleSpinBox, QPushButton)
from PyQt6.QtCore import Qt
from utils.config import load_config, save_config, validate_config

class ConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_values()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Rating Settings
        layout.addWidget(QLabel(""))
        
        rating_layout = QHBoxLayout()
        self.baseline_spin = QDoubleSpinBox()
        self.baseline_spin.setRange(0, 5)
        self.baseline_spin.setSingleStep(0.1)
        rating_layout.addWidget(QLabel("Rating Baseline"))
        rating_layout.addWidget(self.baseline_spin)
        
        self.multiplier_spin = QSpinBox()
        self.multiplier_spin.setRange(1, 100)
        rating_layout.addWidget(QLabel("Rating Multiplier"))
        rating_layout.addWidget(self.multiplier_spin)
        layout.addLayout(rating_layout)
        
        # Length Settings
        layout.addWidget(QLabel(""))
        
        length_layout = QHBoxLayout()
        self.target_spin = QSpinBox()
        self.target_spin.setRange(1000, 1000000)
        self.target_spin.setSingleStep(1000)
        length_layout.addWidget(QLabel("Target Wordcount:"))
        length_layout.addWidget(self.target_spin)
        
        self.penalty_spin = QSpinBox()
        self.penalty_spin.setRange(100, 10000)
        self.penalty_spin.setSingleStep(100)
        length_layout.addWidget(QLabel("Penalty Step:"))
        length_layout.addWidget(self.penalty_spin)
        layout.addLayout(length_layout)
        
        # Member Penalties
        layout.addWidget(QLabel(""))
        
        penalties_layout = QHBoxLayout()
        self.last_penalty_spin = QSpinBox()
        self.last_penalty_spin.setRange(-100, 0)
        penalties_layout.addWidget(QLabel("Penalty 1:"))
        penalties_layout.addWidget(self.last_penalty_spin)
        
        self.second_penalty_spin = QSpinBox()
        self.second_penalty_spin.setRange(-100, 0)
        penalties_layout.addWidget(QLabel("Penalty 2:"))
        penalties_layout.addWidget(self.second_penalty_spin)
        
        self.third_penalty_spin = QSpinBox()
        self.third_penalty_spin.setRange(-100, 0)
        penalties_layout.addWidget(QLabel("Penalty 3:"))
        penalties_layout.addWidget(self.third_penalty_spin)
        layout.addLayout(penalties_layout)
        
        # Save Button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_values)
        layout.addWidget(save_btn)
        
        layout.addStretch()

    def load_values(self):
        """Load current values from config file."""
        config = load_config()
        
        self.baseline_spin.setValue(config["rating"]["baseline"])
        self.multiplier_spin.setValue(config["rating"]["multiplier"])
        
        self.target_spin.setValue(config["length"]["target"])
        self.penalty_spin.setValue(config["length"]["penalty_step"])
        
        self.last_penalty_spin.setValue(config["member_penalties"]["last_selection"])
        self.second_penalty_spin.setValue(config["member_penalties"]["second_last"])
        self.third_penalty_spin.setValue(config["member_penalties"]["third_last"])

    def save_values(self):
        """Save current values to config file."""
        new_config = {
            "rating": {
                "baseline": self.baseline_spin.value(),
                "multiplier": self.multiplier_spin.value()
            },
            "length": {
                "target": self.target_spin.value(),
                "penalty_step": self.penalty_spin.value()
            },
            "member_penalties": {
                "last_selection": self.last_penalty_spin.value(),
                "second_last": self.second_penalty_spin.value(),
                "third_last": self.third_penalty_spin.value()
            }
        }
        
        if validate_config(new_config):
            save_config(new_config)
            if self.parent:
                self.parent.statusBar().showMessage("Configuration saved successfully!", 3000)
        else:
            if self.parent:
                self.parent.statusBar().showMessage("Error: Invalid configuration!", 3000)