import time
from core.adb import tap
from core.actions import click, click_when_found
from core.actions import exists
from core.adb import screenshot
from core.vision import check_pixels
from core.adb import swipe
from core.ocr import find_text
import cv2
def gold_full(device):

    screen_path = screenshot(device)

    pixels = [
        (1294, 63, (231, 192, 13)),
        (1293, 60, (231, 192, 13)),
        (1297, 68, (231, 192, 13))
    ]

    return check_pixels(screen_path, pixels)
def elixir_full(device):

    screen_path = screenshot(device)

    pixels = [
        (1298, 143, (192, 39, 192)),
        (1299, 147, (192, 39, 192)),
        (1299, 149, (192, 39, 192))
    ]

    return check_pixels(screen_path, pixels)

def upgrade_gold(device,count,thread):
# nhớ bán hết nhẫn up tường
    if count ==10:
        if not open_wall(device):
            print("open_wall() thất bại")
            return False
        time.sleep(0.9)
        print("Tap upgrade more")
        tap(device,805,725)
        time.sleep(0.9)
        print("Tap upgrade x10")
        tap(device,630,725)
        print('tap upgrade by gold')
        tap(device,1000, 725)
        time.sleep(0.9)
        print("tap OKay")
        tap(device,1000, 580)
        time.sleep(0.9)
        thread.wall_gold += 10
        thread.wall_gold_changed.emit(thread.wall_gold)
        print("đã nâng cấp 10 tường")
        click(device,"return_home")
    else:
        for i in range(count):
            print(f"Upgrade lần {i+1}")

            if not open_wall(device):
                print("open_wall() thất bại")
                return False
            time.sleep(0.5)
            print("Tap upgrade")
            tap(device,1000, 720)
            time.sleep(1)
            print("Tap confirm")
            tap(device,1120, 800)
            thread.wall_gold += 1
            thread.wall_gold_changed.emit(thread.wall_gold)
        click(device,"return_home")
def upgrade_elixir(device,count,thread):
    if count ==10:
        if not open_wall(device):
            print("open_wall() thất bại")
            return False
        time.sleep(0.8)
        print("Tap upgrade more")
        tap(device,805,725)
        time.sleep(0.9)
        print("Tap upgrade x10")
        tap(device,630,725)
        print('tap upgrade by gold')
        tap(device,1150, 725)
        time.sleep(0.9)
        print("tap OKay")
        tap(device,1000, 580)
        time.sleep(0.9)
        thread.wall_elixir += 10
        thread.wall_elixir_changed.emit(thread.wall_elixir)
        print("đã nâng cấp 10 tường")
        click(device,"return_home")
    else:
        for i in range(count):
            print(f"Upgrade lần {i+1}")

            if not open_wall(device):
                print("open_wall() thất bại")
                return False
            time.sleep(0.8)
            print("Tap upgrade")
            tap(device,1150, 720)

            time.sleep(1)

            print("Tap confirm")
            tap(device,1120, 800)
            thread.wall_elixir += 1
            thread.wall_elixir_changed.emit(thread.wall_elixir)
        click(device,"return_home")


def open_wall(device):

    print("Kiểm tra nâng tường...")

    if not click_when_found(device,"builder", timeout=5):
        print("Không tìm thấy Builder")
        return False

    time.sleep(1)

    if not find_wall(device):
        print("Không tìm thấy Wall sau khi cuộn")
        click(device,"return_home")
        return False

    time.sleep(1)

    return True
def find_wall(device, max_scroll=8):
    time.sleep(0.8)
    for i in range(max_scroll):

        screen_path = screenshot(device)

        screen = cv2.imread(screen_path)

        roi = screen[200:900, 250:690]

        pos, conf = find_text(
        roi,
        "Wall",
        min_conf=0.4,
        debug=True
        )
        if pos:
            x = pos[0] + 250
            y = pos[1] + 200

            print(f"Đã tìm thấy wall ({conf:.2f})")

            tap(device, x, y)
            return True

        print(f"Chưa thấy Wall, cuộn lần {i+1}")

        swipe(device, 634, 536, 643, 142, 1000)

        time.sleep(1)

    return False


    