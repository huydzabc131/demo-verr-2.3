import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from bot import Bot


bots = []

bot1 = Bot("emulator-5554", "Bot 1")
bots.append(bot1)

#bot2 = Bot("emulator-5556", "Bot 2")
#bots.append(bot2)

app = QApplication(sys.argv)

window = MainWindow(bots)
window.show()

app.exec()