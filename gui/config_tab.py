"""Module for the configuration interface."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSpinBox, QDoubleSpinBox, QPushButton, QGridLayout,
                           QFrame, QSizePolicy)
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
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Add some padding around the edges
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Ensure the whole layout aligns to the top

        # Left column - Settings
        settings_widget = QWidget()
        settings_layout = QGridLayout(settings_widget)
        settings_layout.setHorizontalSpacing(20)  # Space between labels and inputs    
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align settings to the top

        # Create and configure all spin boxes
        self.baseline_spin = QDoubleSpinBox()
        self.baseline_spin.setRange(0, 5)
        self.baseline_spin.setSingleStep(0.1)
        
        self.multiplier_spin = QSpinBox()
        self.multiplier_spin.setRange(1, 100)
        
        self.target_spin = QSpinBox()
        self.target_spin.setRange(1000, 1000000)
        self.target_spin.setSingleStep(1000)
        
        self.penalty_spin = QSpinBox()
        self.penalty_spin.setRange(100, 10000)
        self.penalty_spin.setSingleStep(100)
        
        self.last_penalty_spin = QSpinBox()
        self.last_penalty_spin.setRange(-100, 0)
        
        self.second_penalty_spin = QSpinBox()
        self.second_penalty_spin.setRange(-100, 0)
        
        self.third_penalty_spin = QSpinBox()
        self.third_penalty_spin.setRange(-100, 0)

        current_row = 0

        # Rating Settings Section
        rating_header = QLabel("Rating Settings")
        rating_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px 0;")
        settings_layout.addWidget(rating_header, current_row, 0, 1, 2)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Rating Baseline:"), current_row, 0)
        settings_layout.addWidget(self.baseline_spin, current_row, 1)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Rating Multiplier:"), current_row, 0)
        settings_layout.addWidget(self.multiplier_spin, current_row, 1)
        current_row += 1

        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        settings_layout.addWidget(separator1, current_row, 0, 1, 2)
        current_row += 1

        # Length Settings Section
        length_header = QLabel("Length Settings")
        length_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px 0;")
        settings_layout.addWidget(length_header, current_row, 0, 1, 2)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Target Wordcount:"), current_row, 0)
        settings_layout.addWidget(self.target_spin, current_row, 1)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Penalty Step:"), current_row, 0)
        settings_layout.addWidget(self.penalty_spin, current_row, 1)
        current_row += 1

        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        settings_layout.addWidget(separator2, current_row, 0, 1, 2)
        current_row += 1

        # Member Penalties Section
        penalties_header = QLabel("Member Penalties")
        penalties_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px 0;")
        settings_layout.addWidget(penalties_header, current_row, 0, 1, 2)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Penalty 1:"), current_row, 0)
        settings_layout.addWidget(self.last_penalty_spin, current_row, 1)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Penalty 2:"), current_row, 0)
        settings_layout.addWidget(self.second_penalty_spin, current_row, 1)
        current_row += 1
        
        settings_layout.addWidget(QLabel("  Penalty 3:"), current_row, 0)
        settings_layout.addWidget(self.third_penalty_spin, current_row, 1)
        current_row += 1

        # Save Button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_values)
        settings_layout.addWidget(save_btn, current_row, 0, 1, 2)

        # Add settings widget to main layout
        main_layout.addWidget(settings_widget)

        # Right column - Guide
        guide_layout = QVBoxLayout()
        guide_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align guide to the top

        guide_header = QLabel("Configuration Guide")
        guide_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 14px 0;")
        guide_layout.addWidget(guide_header)
        
        guide_text = QLabel("""- Rating Baseline sets the star rating that equals 0 points 
  (lower and higher subtracts or adds points)

- Rating Multiplier is the factor to multiply by 
  (10 is 1 point per 0.1 rating / 3 stars = 30 points)




- Target Wordcount sets the ideal number of words that equals 0 points
  (lower and higher than target wordcount will subtracts points)

- Penalty Step is how many words outside target to apply a 1 point penalty
  (every x number of words outside of target subtracts 1 point)




- Penalty 1, 2, and 3 subtracts points based on who selected recent books
  (1 being the most recent, 2 the second most, 3 the third most)
        """)
        guide_text.setWordWrap(True)
        guide_layout.addWidget(guide_text)
        
        # Add guide layout to main layout
        main_layout.addLayout(guide_layout)

        # Ensure both columns stretch evenly horizontally
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

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
                self.parent.statusBar().setStyleSheet("color: green;")
                self.parent.statusBar().showMessage(" Configuration saved successfully!", 6000)
        else:
            if self.parent:
                self.parent.statusBar().setStyleSheet("color: red;")
                self.parent.statusBar().showMessage(" Error: Invalid configuration!", 6000)