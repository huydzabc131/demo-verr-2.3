import time
import win32api
import win32con
import win32gui


def run_ld_macro(window_title="LDPlayer"):
    """
    Đưa cửa sổ LDPlayer lên trước và gửi tổ hợp Shift + F8
    (Macro trong LDPlayer đã được gán với Shift + F8)
    """

    hwnd = win32gui.FindWindow(None, window_title)

    if hwnd == 0:
        raise RuntimeError(f"Không tìm thấy cửa sổ: {window_title}")

    # Khôi phục nếu đang thu nhỏ
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    # Đưa cửa sổ lên trước
    win32gui.SetForegroundWindow(hwnd)

    time.sleep(0.2)

    # Shift Down
    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)

    time.sleep(0.02)

    # F8 Down
    win32api.keybd_event(win32con.VK_F8, 0, 0, 0)

    time.sleep(0.05)

    # F8 Up
    win32api.keybd_event(win32con.VK_F8, 0, win32con.KEYEVENTF_KEYUP, 0)

    # Shift Up
    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

    time.sleep(0.1)