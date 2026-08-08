import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QScrollArea
)
from PySide6.QtCore import Signal


class WallTab(QWidget):
    config_changed = Signal()

    def __init__(self):
        super().__init__()
        self._is_loading = False

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(14)

        wall_group = QGroupBox("🧱 Wall Auto Upgrade Configuration")
        wall_layout = QFormLayout()
        wall_layout.setContentsMargins(16, 20, 16, 16)
        wall_layout.setSpacing(14)

        self.enable = QCheckBox("Enable Wall Auto Upgrade Routine")

        self.resource = QComboBox()
        self.resource.addItems([
            "Auto",
            "Gold",
            "Elixir"
        ])

        self.count = QSpinBox()
        self.count.setRange(1, 100)
        self.count.setValue(4)

        wall_layout.addRow(self.enable)
        wall_layout.addRow("Resource Type:", self.resource)
        wall_layout.addRow("Wall Batch Count:", self.count)

        wall_group.setLayout(wall_layout)

        main_layout.addWidget(wall_group)
        main_layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

        # Connect signals
        self.enable.toggled.connect(self._on_field_changed)
        self.resource.currentTextChanged.connect(self._on_field_changed)
        self.count.valueChanged.connect(self._on_field_changed)


    def _on_field_changed(self):
        if not self._is_loading:
            self.save_config_data()
            self.config_changed.emit()

    def apply_data(self, data: dict):
        self._is_loading = True
        try:
            if "wall_enable" in data:
                self.enable.setChecked(bool(data["wall_enable"]))
            if "wall_resource" in data:
                idx = self.resource.findText(str(data["wall_resource"]))
                if idx >= 0:
                    self.resource.setCurrentIndex(idx)
            if "wall_count" in data:
                self.count.setValue(int(data["wall_count"]))
        finally:
            self._is_loading = False

    def load_config_data(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.apply_data(data)
        except Exception as e:
            print("Error loading wall_tab config:", e)

    def save_config_data(self):
        try:
            data = {}
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass

            data["wall_enable"] = self.enable.isChecked()
            data["wall_resource"] = self.resource.currentText()
            data["wall_count"] = self.count.value()

            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error saving wall_tab config:", e)
