# core/ocr.py

import cv2
import easyocr

# Khởi tạo OCR một lần
reader = easyocr.Reader(['en'], gpu=False)


def preprocess(image):
    """
    Tiền xử lý ảnh trước khi OCR.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return gray


def read_text(image):
    """
    Đọc toàn bộ text trong ảnh.
    """
    image = preprocess(image)

    results = reader.readtext(image)

    if not results:
        return ""

    text = ""

    for _, value, _ in results:
        text += value

    return text


def find_text(image, target, min_conf=0.5, debug=False):
    """
    Tìm text trong ảnh.

    Returns:
        (x, y), confidence
    hoặc:
        None, None
    """

    image = preprocess(image)

    results = reader.readtext(image)

    if debug:
        print("===== OCR =====")

    for bbox, text, conf in results:

        if debug:
            print(f"'{text}'  conf={conf:.2f}")

        if conf < min_conf:
            continue

        # So khớp không phân biệt hoa thường
        if target.lower() in text.lower():

            x = int((bbox[0][0] + bbox[2][0]) / 2)
            y = int((bbox[0][1] + bbox[2][1]) / 2)

            return (x, y), conf

    return None, None