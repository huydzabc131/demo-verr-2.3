import json
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal


class BattleTab(QWidget):
    config_changed = Signal()

    def __init__(self):
        super().__init__()
        self._is_loading = False

        # Outer layout containing the scroll area for 100% responsiveness on small screens
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(14)

        # --- Group 1: General Strategy & Delay ---
        strategy_group = QGroupBox("⚔️ General Strategy")
        strategy_layout = QFormLayout()
        strategy_layout.setContentsMargins(14, 18, 14, 14)
        strategy_layout.setSpacing(12)

        self.side = QComboBox()
        self.side.addItems([
            "Random",
            "Left",
            "Right"
        ])

        self.delay = QSpinBox()
        self.delay.setRange(1, 20)
        self.delay.setValue(5)
        self.delay.setSuffix(" s")

        self.return_home_delay = QSpinBox()
        self.return_home_delay.setRange(0, 60)
        self.return_home_delay.setSingleStep(1)
        self.return_home_delay.setValue(5)
        self.return_home_delay.setSuffix(" s")

        strategy_layout.addRow("Attack Side:", self.side)
        strategy_layout.addRow("Deploy Delay:", self.delay)
        strategy_layout.addRow("Return Home Delay:", self.return_home_delay)
        strategy_group.setLayout(strategy_layout)

        # --- Group 2: Loot Filter ---
        loot_group = QGroupBox("💰 Loot Filter")
        loot_layout = QFormLayout()
        loot_layout.setContentsMargins(14, 18, 14, 14)
        loot_layout.setSpacing(12)

        self.loot_enable = QCheckBox("Enable Loot Filter")
        self.loot_enable.setChecked(True)

        self.min_gold = QSpinBox()
        self.min_gold.setRange(0, 2000000)
        self.min_gold.setSingleStep(50000)
        self.min_gold.setValue(700000)

        self.min_elixir = QSpinBox()
        self.min_elixir.setRange(0, 2000000)
        self.min_elixir.setSingleStep(50000)
        self.min_elixir.setValue(700000)

        self.loot_mode = QComboBox()
        self.loot_mode.addItems([
            "AND",
            "OR"
        ])

        loot_layout.addRow(self.loot_enable)
        loot_layout.addRow("Minimum Gold:", self.min_gold)
        loot_layout.addRow("Minimum Elixir:", self.min_elixir)
        loot_layout.addRow("Condition Mode:", self.loot_mode)
        loot_group.setLayout(loot_layout)

        # --- Group 3: Hero Deploy ---
        hero_group = QGroupBox("👑 Hero & Champion Deploy Configuration")
        hero_main_layout = QVBoxLayout()
        hero_main_layout.setContentsMargins(14, 18, 14, 14)
        hero_main_layout.setSpacing(12)

        # Quick action row for select all/none
        hero_quick_row = QHBoxLayout()
        hero_quick_label = QLabel("Active Deployment Roster:")
        hero_quick_label.setStyleSheet("color: #A1A1AA; font-weight: 600;")
        
        select_all_btn = QPushButton("✓ Select All")
        select_all_btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        select_all_btn.clicked.connect(self._select_all_heroes)

        clear_all_btn = QPushButton("✗ Clear All")
        clear_all_btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        clear_all_btn.clicked.connect(self._clear_all_heroes)

        hero_quick_row.addWidget(hero_quick_label)
        hero_quick_row.addStretch()
        hero_quick_row.addWidget(select_all_btn)
        hero_quick_row.addWidget(clear_all_btn)

        hero_grid = QGridLayout()
        hero_grid.setSpacing(14)

        self.hero_king = QCheckBox("Barbarian King")
        self.hero_queen = QCheckBox("Archer Queen")
        self.hero_warden = QCheckBox("Grand Warden")
        self.hero_royal = QCheckBox("Royal Champion")
        self.hero_prince = QCheckBox("Minion Prince")
        self.hero_duke = QCheckBox("Grand Duke")

        # Values
        self.hero_king.setChecked(True)
        self.hero_queen.setChecked(True)
        self.hero_warden.setChecked(True)
        self.hero_royal.setChecked(True)
        self.hero_prince.setChecked(False)
        self.hero_duke.setChecked(False)

        hero_grid.addWidget(self.hero_king,   0, 0)
        hero_grid.addWidget(self.hero_royal,  0, 1)

        hero_grid.addWidget(self.hero_queen,  1, 0)
        hero_grid.addWidget(self.hero_prince, 1, 1)

        hero_grid.addWidget(self.hero_warden, 2, 0)
        hero_grid.addWidget(self.hero_duke,   2, 1)

        hero_main_layout.addLayout(hero_quick_row)
        hero_main_layout.addLayout(hero_grid)
        hero_group.setLayout(hero_main_layout)

        # Combine top groups horizontally or stack cleanly based on screen space
        top_row = QHBoxLayout()
        top_row.setSpacing(14)
        top_row.addWidget(strategy_group)
        top_row.addWidget(loot_group)

        main_layout.addLayout(top_row)
        main_layout.addWidget(hero_group)
        main_layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

        # Connect signals for auto-saving config and change notification
        self.side.currentTextChanged.connect(self._on_field_changed)
        self.delay.valueChanged.connect(self._on_field_changed)
        self.return_home_delay.valueChanged.connect(self._on_field_changed)
        self.loot_enable.toggled.connect(self._on_field_changed)
        self.min_gold.valueChanged.connect(self._on_field_changed)
        self.min_elixir.valueChanged.connect(self._on_field_changed)
        self.loot_mode.currentTextChanged.connect(self._on_field_changed)

        self.hero_king.toggled.connect(self._on_field_changed)
        self.hero_queen.toggled.connect(self._on_field_changed)
        self.hero_warden.toggled.connect(self._on_field_changed)
        self.hero_royal.toggled.connect(self._on_field_changed)
        self.hero_prince.toggled.connect(self._on_field_changed)
        self.hero_duke.toggled.connect(self._on_field_changed)


    def _on_field_changed(self):
        if not self._is_loading:
            self.save_config_data()
            self.config_changed.emit()

    def _select_all_heroes(self):
        self.hero_king.setChecked(True)
        self.hero_queen.setChecked(True)
        self.hero_warden.setChecked(True)
        self.hero_royal.setChecked(True)
        self.hero_prince.setChecked(True)
        self.hero_duke.setChecked(True)
        self._on_field_changed()

    def _clear_all_heroes(self):
        self.hero_king.setChecked(False)
        self.hero_queen.setChecked(False)
        self.hero_warden.setChecked(False)
        self.hero_royal.setChecked(False)
        self.hero_prince.setChecked(False)
        self.hero_duke.setChecked(False)
        self._on_field_changed()

    def apply_data(self, data: dict):
        self._is_loading = True
        try:
            if "attack_side" in data:
                idx = self.side.findText(str(data["attack_side"]))
                if idx >= 0:
                    self.side.setCurrentIndex(idx)
            if "deploy_delay" in data:
                self.delay.setValue(int(data["deploy_delay"]))
            if "return_home_delay" in data:
                self.return_home_delay.setValue(int(data["return_home_delay"]))
            if "loot_enable" in data:
                self.loot_enable.setChecked(bool(data["loot_enable"]))
            if "min_gold" in data:
                self.min_gold.setValue(int(data["min_gold"]))
            if "min_elixir" in data:
                self.min_elixir.setValue(int(data["min_elixir"]))
            if "loot_mode" in data:
                idx = self.loot_mode.findText(str(data["loot_mode"]))
                if idx >= 0:
                    self.loot_mode.setCurrentIndex(idx)
            if "heroes" in data and isinstance(data["heroes"], dict):
                heroes = data["heroes"]
                if "king" in heroes: self.hero_king.setChecked(bool(heroes["king"]))
                if "queen" in heroes: self.hero_queen.setChecked(bool(heroes["queen"]))
                if "warden" in heroes: self.hero_warden.setChecked(bool(heroes["warden"]))
                if "royal_champion" in heroes: self.hero_royal.setChecked(bool(heroes["royal_champion"]))
                if "minion_prince" in heroes: self.hero_prince.setChecked(bool(heroes["minion_prince"]))
                if "duke" in heroes: self.hero_duke.setChecked(bool(heroes["duke"]))
        finally:
            self._is_loading = False

    def load_config_data(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.apply_data(data)
        except Exception as e:
            print("Error loading battle_tab config:", e)

    def save_config_data(self):
        try:
            data = {}
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass

            data["attack_side"] = self.side.currentText()
            data["deploy_delay"] = self.delay.value()
            data["return_home_delay"] = self.return_home_delay.value()
            data["loot_enable"] = self.loot_enable.isChecked()
            data["min_gold"] = self.min_gold.value()
            data["min_elixir"] = self.min_elixir.value()
            data["loot_mode"] = self.loot_mode.currentText()
            data["heroes"] = {
                "king": self.hero_king.isChecked(),
                "queen": self.hero_queen.isChecked(),
                "warden": self.hero_warden.isChecked(),
                "royal_champion": self.hero_royal.isChecked(),
                "minion_prince": self.hero_prince.isChecked(),
                "duke": self.hero_duke.isChecked(),
            }

            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error saving battle_tab config:", e)


        