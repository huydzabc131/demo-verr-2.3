import cv2
import re

from core.adb import screenshot
from core.ocr import read_text

# =========================
# ROI
# =========================

GOLD_ROI = (120, 158, 76, 222)
ELIXIR_ROI = (171, 212, 77, 222)



def parse_number(text):
    """
    Chuyển chuỗi OCR thành số nguyên.
    Ví dụ:
        '853,000' -> 853000
        '8O3OOO'  -> 803000
    """

    if text is None:
        return 0

    text = text.replace("O", "0")
    text = text.replace("o", "0")

    digits = re.sub(r"\D", "", text)

    if digits == "":
        return 0

    return int(digits)


def read_resource(screen, roi):

    y1, y2, x1, x2 = roi

    crop = screen[y1:y2, x1:x2]

    text = read_text(crop)

    value = parse_number(text)

    return value


def read_resources(device):
    """
    Đọc toàn bộ tài nguyên của đối thủ.
    """

    screen_path = screenshot(device)

    screen = cv2.imread(screen_path)

    gold = read_resource(screen, GOLD_ROI)

    elixir = read_resource(screen, ELIXIR_ROI)


    return {
        "gold": gold,
        "elixir": elixir,
        
    }


def should_attack(resources,
                  min_gold,
                  min_elixir,
                  mode):
    """
    Kiểm tra có nên tấn công hay không.
    """

    gold_ok = resources["gold"] >= min_gold
    elixir_ok = resources["elixir"] >= min_elixir

    if mode == "AND":
        return gold_ok and elixir_ok
    elif mode == "OR":
        return gold_ok or elixir_ok

    # Mặc định nếu mode không hợp lệ
    return gold_ok and elixir_ok