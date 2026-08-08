from PySide6.QtWidgets import (
    QGroupBox,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGridLayout,
    QScrollArea,
    QCheckBox
)
from PySide6.QtCore import Qt


class StatisticsTab(QWidget):

    def __init__(self):
        super().__init__()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(16)

        title = QLabel("📊 Real-time Session Statistics")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #F4F4F5;")

        # Card container grid
        cards_layout = QGridLayout()
        cards_layout.setSpacing(14)

        # Card 1: Attacks
        attack_card = QFrame()
        attack_card.setObjectName("statCard")
        attack_card.setStyleSheet("""
            QFrame#statCard {
                background-color: #18181B;
                border: 1px solid #27272A;
                border-radius: 10px;
                padding: 16px;
            }
            QFrame#statCard:hover {
                border-color: #3B82F6;
            }
        """)
        attack_card_layout = QVBoxLayout(attack_card)
        attack_card_layout.setSpacing(6)
        attack_icon_label = QLabel("⚔️ Total Attacks Completed")
        attack_icon_label.setStyleSheet("color: #A1A1AA; font-size: 12px; font-weight: 600;")
        self.attack = QLabel("Attacks : 0")
        self.attack.setStyleSheet("color: #60A5FA; font-size: 18px; font-weight: 800;")
        attack_card_layout.addWidget(attack_icon_label)
        attack_card_layout.addWidget(self.attack)

        # Card 2: Wall Gold
        gold_card = QFrame()
        gold_card.setObjectName("statCard")
        gold_card.setStyleSheet("""
            QFrame#statCard {
                background-color: #18181B;
                border: 1px solid #27272A;
                border-radius: 10px;
                padding: 16px;
            }
            QFrame#statCard:hover {
                border-color: #FBBF24;
            }
        """)
        gold_card_layout = QVBoxLayout(gold_card)
        gold_card_layout.setSpacing(6)
        gold_icon_label = QLabel("🟡 Walls Upgraded (Gold)")
        gold_icon_label.setStyleSheet("color: #A1A1AA; font-size: 12px; font-weight: 600;")
        self.wall_gold = QLabel("Wall Upgraded (Gold) : 0")
        self.wall_gold.setStyleSheet("color: #FBBF24; font-size: 18px; font-weight: 800;")
        gold_card_layout.addWidget(gold_icon_label)
        gold_card_layout.addWidget(self.wall_gold)

        # Card 3: Wall Elixir
        elixir_card = QFrame()
        elixir_card.setObjectName("statCard")
        elixir_card.setStyleSheet("""
            QFrame#statCard {
                background-color: #18181B;
                border: 1px solid #27272A;
                border-radius: 10px;
                padding: 16px;
            }
            QFrame#statCard:hover {
                border-color: #C084FC;
            }
        """)
        elixir_card_layout = QVBoxLayout(elixir_card)
        elixir_card_layout.setSpacing(6)
        elixir_icon_label = QLabel("🟣 Walls Upgraded (Elixir)")
        elixir_icon_label.setStyleSheet("color: #A1A1AA; font-size: 12px; font-weight: 600;")
        self.wall_elixir = QLabel("Wall Upgraded (Elixir) : 0")
        self.wall_elixir.setStyleSheet("color: #C084FC; font-size: 18px; font-weight: 800;")
        elixir_card_layout.addWidget(elixir_icon_label)
        elixir_card_layout.addWidget(self.wall_elixir)

        cards_layout.addWidget(attack_card, 0, 0)
        cards_layout.addWidget(gold_card, 0, 1)
        cards_layout.addWidget(elixir_card, 0, 2)

        main_layout.addWidget(title)
        main_layout.addLayout(cards_layout)
    # ==========================
# Account Manager
# ==========================

        account_group = QGroupBox("🔄 Account Manager")
        account_group.setStyleSheet("""
        QGroupBox {
            color: #F4F4F5;
            font-size: 14px;
            font-weight: 700;
            border: 1px solid #27272A;
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 12px;
            background-color: #18181B;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }
        """)

        account_layout = QVBoxLayout(account_group)
        account_layout.setSpacing(10)

        self.enable = QCheckBox("Enable Account Manager")
        self.enable.setStyleSheet("""
        QCheckBox {
            color: #F4F4F5;
            font-size: 13px;
            font-weight: 600;
        }
        """)

        self.reset_when_finished = QCheckBox("Reset when all accounts are finished")
        self.reset_when_finished.setChecked(True)
        self.reset_when_finished.setStyleSheet("""
        QCheckBox {
            color: #F4F4F5;
            font-size: 13px;
            font-weight: 600;
        }
        """)

        account_layout.addWidget(self.enable)
        account_layout.addWidget(self.reset_when_finished)

        main_layout.addWidget(account_group)
        main_layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

    def update_attack(self, value):
        self.attack.setText(f"Attacks : {value}")

    def update_wall_gold(self, value):
        self.wall_gold.setText(
            f"Wall Upgraded (Gold) : {value}"
        )

    def update_wall_elixir(self, value):
        self.wall_elixir.setText(
            f"Wall Upgraded (Elixir) : {value}"
        )

