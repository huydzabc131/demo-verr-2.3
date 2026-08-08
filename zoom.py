import win32gui
import win32api
import win32con


class LDZoom:

    def __init__(self, window_title="LDPlayer"):
        self.hwnd = win32gui.FindWindow(None, window_title)

        if self.hwnd == 0:
            raise Exception("Không tìm thấy cửa sổ LDPlayer")

    def zoom(self, delta=120):

        # Lấy kích thước client
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)

        x = (right - left) // 2
        y = (bottom - top) // 2

        lParam = (y << 16) | x
        wParam = (delta << 16) | win32con.MK_CONTROL

        # Ctrl Down
        win32api.PostMessage(
            self.hwnd,
            win32con.WM_KEYDOWN,
            win32con.VK_CONTROL,
            0
        )

        # Wheel
        win32api.PostMessage(
            self.hwnd,
            win32con.WM_MOUSEWHEEL,
            wParam,
            lParam
        )

        # Ctrl Up
        win32api.PostMessage(
            self.hwnd,
            win32con.WM_KEYUP,
            win32con.VK_CONTROL,
            0
        )

    def zoom_in(self):
        self.zoom(120)

    def zoom_out(self):
        self.zoom(-500)