from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QLabel,
    QPlainTextEdit,
    QFrame,
    QGroupBox,
    QSplitter,
    QSizePolicy
)
from PySide6.QtCore import Qt
from gui.battle_tab import BattleTab
from gui.wall_tab import WallTab
from bot_thread import BotThread
from gui.statistics_tab import StatisticsTab
from gui.live_tab import LiveTab
from gui.strategy_tab import StrategyTab
from gui.console_tab import ConsoleTab
from gui.screen_thead import ScreenThread
from core.config_manager import ConfigProfileManager
from gui.profile_bar import ProfileBar


class BotPage(QWidget):

    def __init__(self, bot):
        super().__init__()

        self.bot = bot
        self.screen_thread = None
        self.config_manager = ConfigProfileManager()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Top Header & Action Control Bar ---
        top_card = QFrame()
        top_card.setObjectName("topCard")
        top_card.setStyleSheet("""
            QFrame#topCard {
                background-color: #18181B;
                border: 1px solid #27272A;
                border-radius: 10px;
                padding: 6px 12px;
            }
        """)
        top_layout = QHBoxLayout(top_card)
        top_layout.setContentsMargins(8, 4, 8, 4)

        # Bot Info & Stat Pill
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)

        device_info = QLabel(f"📱 {self.bot.name} ({self.bot.device})")
        device_info.setStyleSheet("font-size: 14px; font-weight: 700; color: #F4F4F5;")

        self.attack_label = QLabel("Attacks : 0")
        self.attack_label.setStyleSheet("""
            background-color: #09090B;
            color: #60A5FA;
            font-weight: 700;
            font-size: 12px;
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid #27272A;
        """)

        info_layout.addWidget(device_info)
        info_layout.addWidget(self.attack_label)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton("▶ Start Bot")
        self.start_btn.setMinimumHeight(34)
        self.start_btn.setMinimumWidth(110)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: 700;
                border-radius: 6px;
                border: none;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)

        self.stop_btn = QPushButton("⏹ Stop Bot")
        self.stop_btn.setMinimumHeight(34)
        self.stop_btn.setMinimumWidth(110)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                font-weight: 700;
                border-radius: 6px;
                border: none;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)

        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        top_layout.addLayout(info_layout)
        top_layout.addStretch()
        top_layout.addLayout(btn_layout)

        main_layout.addWidget(top_card)

        # --- Configuration Profile Manager Bar ---
        self.profile_bar = ProfileBar(
            manager=self.config_manager,
            get_current_ui_config=self.get_current_ui_config,
            apply_config_to_ui=self.apply_config_to_ui,
            parent=self
        )
        main_layout.addWidget(self.profile_bar)

        # --- Center Configuration Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #27272A;
                border-radius: 8px;
                background-color: #18181B;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #09090B;
                color: #A1A1AA;
                padding: 8px 18px;
                font-weight: 600;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                border: 1px solid #27272A;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #18181B;
                color: #60A5FA;
                border-bottom: 2px solid #3B82F6;
            }
            QTabBar::tab:hover:!selected {
                background-color: #27272A;
                color: #F4F4F5;
            }
        """)

        self.battle_tab = BattleTab()
        self.wall_tab = WallTab()
        self.live_tab = LiveTab(self.bot.device)
        self.strategy_tab = StrategyTab(self.bot.device)
        self.statistics_tab = StatisticsTab()
        self.console_tab = ConsoleTab()

        self.tabs.addTab(self.battle_tab, "⚔️ Battle Strategy")
        self.tabs.addTab(self.wall_tab, "🧱 Wall Upgrade")
        self.tabs.addTab(self.live_tab, "🎯 Live Deployment")
        self.tabs.addTab(self.strategy_tab, "🎲 Strategy Manager")
        self.tabs.addTab(self.statistics_tab, "📊 Session Statistics")
        self.tabs.addTab(self.console_tab, "📜 Console & System Log")

        # Keep property reference for compatibility
        self.log = self.console_tab.log_edit

        main_layout.addWidget(self.tabs, stretch=1)
        self.setLayout(main_layout)

        # Connect UI change signals to mark unsaved profile status
        self.battle_tab.config_changed.connect(self.profile_bar.mark_unsaved)
        self.wall_tab.config_changed.connect(self.profile_bar.mark_unsaved)
        self.live_tab.config_changed.connect(self.profile_bar.mark_unsaved)
        self.strategy_tab.config_changed.connect(self.profile_bar.mark_unsaved)

        self.profile_bar.profile_changed.connect(self.on_profile_loaded)
        self.profile_bar.profile_saved.connect(self.on_profile_saved)

        # Initial load of active profile into UI
        active_prof = self.config_manager.get_active_profile()
        self.apply_config_to_ui(active_prof.to_dict())
        self.profile_bar.mark_saved()

        # Start live screenshot thread continuously for UI visual tabs
        self.ensure_screen_thread()

    def ensure_screen_thread(self):
        if self.screen_thread is None or not self.screen_thread.isRunning():
            self.screen_thread = ScreenThread(self.bot.device)
            self.screen_thread.frame_changed.connect(self.live_tab.update_frame)
            self.screen_thread.frame_changed.connect(self.strategy_tab.update_frame)
            self.screen_thread.start()

    def on_profile_loaded(self, config: dict):
        prof_name = self.config_manager.active_profile_name
        self.log_profile_info(prof_name, config)

    def on_profile_saved(self, config: dict):
        prof_name = self.config_manager.active_profile_name
        actions_cnt = len(config.get("deploy_actions", []))
        self.console_tab.append_log(f"[CONFIG] Saved profile: '{prof_name}' ({actions_cnt} actions)")

    def log_profile_info(self, profile_name: str, config: dict):
        actions_cnt = len(config.get("deploy_actions", []))
        delay = config.get("return_home_delay", 5)
        side = config.get("attack_side", "Random")
        msg = (
            f"[CONFIG] Loading profile: {profile_name}\n"
            f"Deployment System = Live Deploy ({actions_cnt} actions)\n"
            f"Attack Side = {side}\n"
            f"Return Home Delay = {delay}s"
        )
        self.console_tab.append_log(msg)
        print(f"[CONFIG] Loaded profile '{profile_name}' | Live Deploy Actions: {actions_cnt}")

    def get_current_ui_config(self) -> dict:
        strat_data = self.strategy_tab.get_data()
        return {
            "_profile_name": self.config_manager.active_profile_name,
            "attack_side": self.battle_tab.side.currentText(),
            "deploy_delay": self.battle_tab.delay.value(),
            "return_home_delay": self.battle_tab.return_home_delay.value(),

            # Loot Filter
            "loot_enable": self.battle_tab.loot_enable.isChecked(),
            "min_gold": self.battle_tab.min_gold.value(),
            "min_elixir": self.battle_tab.min_elixir.value(),
            "loot_mode": self.battle_tab.loot_mode.currentText(),

            "heroes": {
                "king": self.battle_tab.hero_king.isChecked(),
                "queen": self.battle_tab.hero_queen.isChecked(),
                "warden": self.battle_tab.hero_warden.isChecked(),
                "royal_champion": self.battle_tab.hero_royal.isChecked(),
                "minion_prince": self.battle_tab.hero_prince.isChecked(),
                "duke": self.battle_tab.hero_duke.isChecked(),
            },
            # Wall
            "wall_enable": self.wall_tab.enable.isChecked(),
            "wall_resource": self.wall_tab.resource.currentText(),
            "wall_count": self.wall_tab.count.value(),
            
            "account_manager": {
                "enable": self.statistics_tab.enable.isChecked(),
                "reset_when_finished": self.statistics_tab.reset_when_finished.isChecked(),
},
            # Deployment System
            "random_mode": strat_data.get("random_mode", "Sequential"),
            "random_configs": strat_data.get("random_configs", []),
            "deploy_actions": strat_data.get("deploy_actions", self.live_tab.deploy_actions)
        }

    def apply_config_to_ui(self, config: dict):
        self.battle_tab.apply_data(config)
        self.wall_tab.apply_data(config)
        self.live_tab.apply_data(config)
        self.strategy_tab.apply_data(config)

    def start_bot(self):

        if self.bot.thread is not None:
            return

        config = self.get_current_ui_config()
        active_prof = self.config_manager.active_profile_name
        actions_cnt = len(config.get("deploy_actions", []))

        start_msg = (
            f"[BOT START] Starting Battle Loop...\n"
            f"Current Profile: {active_prof}\n"
            f"Mode: LIVE DEPLOY ({actions_cnt} sequence actions)\n"
        )
        self.console_tab.append_log(start_msg)

        self.ensure_screen_thread()

        # Reset Statistics
        self.statistics_tab.update_attack(0)
        self.statistics_tab.update_wall_gold(0)
        self.statistics_tab.update_wall_elixir(0)

        self.bot.thread = BotThread(self.bot, config)

        self.bot.thread.log.connect(self.add_log)

        # Label Attack cũ
        self.bot.thread.attack_changed.connect(self.update_attack)

        # Statistics
        self.bot.thread.attack_changed.connect(
            self.statistics_tab.update_attack
        )

        self.bot.thread.wall_gold_changed.connect(
            self.statistics_tab.update_wall_gold
        )

        self.bot.thread.wall_elixir_changed.connect(
            self.statistics_tab.update_wall_elixir
        )

        self.console_tab.set_status("🟢 Bot Running", True)
        self.bot.thread.start()

    def stop_bot(self):

        if self.bot.thread is None:
            return

        self.bot.thread.stop()
        self.bot.thread.wait()      # đợi thread kết thúc
        self.bot.thread = None

        self.console_tab.set_status("⚪ Bot Stopped", False)
        print("Bot stopped")

    def add_log(self, text):
        self.console_tab.append_log(text)

    def update_attack(self, count):
        self.attack_label.setText(f"Attacks : {count}")
