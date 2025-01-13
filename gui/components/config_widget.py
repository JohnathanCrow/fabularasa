from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QVBoxLayout, QWidget)

from utils.core.config import load_config, save_config, validate_config


class ConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.profile_manager = parent.profile_manager if parent else None
        self.init_ui()
        self.load_values()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Left column - Settings
        settings_widget = QWidget()
        settings_layout = QGridLayout(settings_widget)
        settings_layout.setHorizontalSpacing(20)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create spin boxes
        self.baseline_spin = QDoubleSpinBox()
        self.baseline_spin.setRange(1, 5)
        self.baseline_spin.setSingleStep(0.1)

        self.multiplier_spin = QSpinBox()
        self.multiplier_spin.setRange(1, 100)

        self.target_spin = QSpinBox()
        self.target_spin.setRange(1000, 1000000)
        self.target_spin.setSingleStep(1000)

        self.penalty_spin = QSpinBox()
        self.penalty_spin.setRange(0, 10000)
        self.penalty_spin.setSingleStep(1000)

        self.last_penalty_spin = QSpinBox()
        self.last_penalty_spin.setRange(-100, 0)

        self.second_penalty_spin = QSpinBox()
        self.second_penalty_spin.setRange(-100, 0)

        self.third_penalty_spin = QSpinBox()
        self.third_penalty_spin.setRange(-100, 0)

        current_row = 0

        # Rating Settings Section
        rating_header = QLabel("Rating Settings")
        rating_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 10px 0;"
        )
        settings_layout.addWidget(rating_header, current_row, 0, 1, 2)
        current_row += 1

        settings_layout.addWidget(QLabel("  Rating Baseline:"), current_row, 0)
        settings_layout.addWidget(self.baseline_spin, current_row, 1)
        current_row += 1

        settings_layout.addWidget(QLabel("  Rating Multiplier:"), current_row, 0)
        settings_layout.addWidget(self.multiplier_spin, current_row, 1)
        current_row += 1

        # Length Settings Section
        length_header = QLabel("Length Settings")
        length_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 10px 0;"
        )
        settings_layout.addWidget(length_header, current_row, 0, 1, 2)
        current_row += 1

        settings_layout.addWidget(QLabel("  Target Words:"), current_row, 0)
        settings_layout.addWidget(self.target_spin, current_row, 1)
        current_row += 1

        settings_layout.addWidget(QLabel("  Penalty Step:"), current_row, 0)
        settings_layout.addWidget(self.penalty_spin, current_row, 1)
        current_row += 1

        # Member Penalties Section
        penalties_header = QLabel("Member Penalties")
        penalties_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 10px 0;"
        )
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
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_values)
        settings_layout.addWidget(save_btn, current_row, 0, 1, 2)

        # Add settings widget to main layout
        main_layout.addWidget(settings_widget)

        # Right column - Guide
        guide_layout = QVBoxLayout()
        guide_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        guide_header = QLabel("Configuration Guide")
        guide_header.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 14px 0;"
        )
        guide_layout.addWidget(guide_header)

        guide_text = QLabel(
            """- Rating Baseline sets the star rating that equals 0 points 
  (lower and higher subtracts or adds points)

- Rating Multiplier is the factor to multiply the rating by 
  (10 is 1 point per 0.1 rating / 3 stars = 20 points at baseline 1)



- Target Words sets the number of words that equals 0 points
  (lower and higher than target wordcount will subtracts points)

- Penalty Step is how many words outside target to apply a 1 point penalty
  (every x number of words outside of target subtracts 1 point)




- Penalty 1, 2, and 3 subtracts points based on who selected recent books
  (1 being the most recent, 2 the second most, 3 the third most)
        """
        )
        guide_text.setWordWrap(True)
        guide_layout.addWidget(guide_text)

        main_layout.addLayout(guide_layout)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

    def load_values(self):
        profile = (
            self.profile_manager.get_current_profile() if self.profile_manager else None
        )
        config = load_config(profile)

        # Clear any existing values first
        self.baseline_spin.setValue(1.0)
        self.multiplier_spin.setValue(1)
        self.target_spin.setValue(1000)
        self.penalty_spin.setValue(0)
        self.last_penalty_spin.setValue(0)
        self.second_penalty_spin.setValue(0)
        self.third_penalty_spin.setValue(0)

        # Set new values
        self.baseline_spin.setValue(config["rating"]["baseline"])
        self.multiplier_spin.setValue(config["rating"]["multiplier"])
        self.target_spin.setValue(config["length"]["target"])
        self.penalty_spin.setValue(config["length"]["penalty_step"])
        self.last_penalty_spin.setValue(config["member_penalties"]["last_selection"])
        self.second_penalty_spin.setValue(config["member_penalties"]["second_last"])
        self.third_penalty_spin.setValue(config["member_penalties"]["third_last"])

    def save_values(self):
        profile = (
            self.profile_manager.get_current_profile() if self.profile_manager else None
        )
        new_config = {
            "rating": {
                "baseline": self.baseline_spin.value(),
                "multiplier": self.multiplier_spin.value(),
            },
            "length": {
                "target": self.target_spin.value(),
                "penalty_step": self.penalty_spin.value(),
            },
            "member_penalties": {
                "last_selection": self.last_penalty_spin.value(),
                "second_last": self.second_penalty_spin.value(),
                "third_last": self.third_penalty_spin.value(),
            },
        }

        if validate_config(new_config):
            save_config(new_config, profile)
            if self.parent:
                self.parent.statusBar().setStyleSheet("color: green;")
                self.parent.statusBar().showMessage(
                    "Configuration saved successfully!", 6000
                )
        elif self.parent:
            self.parent.statusBar().setStyleSheet("color: red;")
            self.parent.statusBar().showMessage("Error: Invalid configuration!", 6000)

    def reload_profile(self):
        self.load_values()
