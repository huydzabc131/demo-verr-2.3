from PySide6.QtCore import QThread, Signal
from battlte import run_once
from datetime import datetime

class BotThread(QThread):
    status_changed = Signal(str)
    log = Signal(str)
    attack_changed = Signal(int) 
    wall_gold_changed = Signal(int)
    wall_elixir_changed = Signal(int)
    def __init__(self, bot, config):
        super().__init__()
        self.attack_count = 0
        self.bot = bot
        self.config = config
        self.running = False
        self.attack_count = 0
        self.wall_gold = 0
        self.wall_elixir = 0

    def run(self):
        self.running = True
        self.status_changed.emit("Running")
        print(f"{self.bot.name} thread bắt đầu")

        while self.running:
            print("Loop:", self.running)

            try:
                run_once(self.bot, self.config, self)

            except Exception as e:
                print(e)
        self.bot.thread = None
        print("Thoát thread")

    def stop(self):
        self.status_changed.emit("Stopped")
        print(f"{self.bot.name} đang dừng thread")
        self.running = False
    def write_log(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.log.emit(f"[{now}] {text}")