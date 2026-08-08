from bot import Bot
import threading
import time


bot1 = Bot("Bot 1")

thread = threading.Thread(
    target=bot1.run,
    daemon=True
)

thread.start()

time.sleep(5)

bot1.stop()

thread.join()