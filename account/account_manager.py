from core.adb import screenshot
from core.ocr import read_text
NAME_X1 = 107
NAME_Y1 = 7
NAME_X2 = 299
NAME_Y2 = 54
import cv2

class AccountManager:
    
    def __init__(self, config):
        self.config = config

        account_cfg = config.get("account_manager", {})

        self.enable = account_cfg.get("enable", False)

        self.current_name_roi = account_cfg.get("current_name_roi", {})

        self.current_account = None

    # ============================
    # OCR Current Account
    # ============================

    



    def read_current_account_name(self, device):

        image_path = screenshot(device)

        screen = cv2.imread(image_path)

        if screen is None:
            print("Failed to read screenshot")
            return None

        name_img = screen[NAME_Y1:NAME_Y2, NAME_X1:NAME_X2]

        raw_name = read_text(name_img)
        name = self.normalize_account_name(raw_name)

        print(f"[OCR RAW] {raw_name}")
        print(f"[OCR NORMALIZED] {name}")

        if not name:
            return None

        return name
    def find_next_account(self, device, current_account):

        image_path = screenshot(device)

        screen = cv2.imread(image_path)

        if screen is None:
            return None


        for roi in self.account_rois:

            x1, y1, x2, y2 = roi

            name_img = screen[434:865, 1124:1462]

            raw_name = read_text(name_img)
            name = self.normalize_account_name(raw_name)


            print(f"[ACCOUNT LIST] {name}")


            if not name:
                continue


            # bỏ qua account hiện tại
            if name == current_account:
                print(f"[SKIP CURRENT] {name}")
                continue


            print(f"[NEXT ACCOUNT] {name}")


            click_x = (x1+x2)//2
            click_y = (y1+y2)//2


            return click_x, click_y, name


        return None
    def read_current_account_List_name(self, device):
    
            image_path = screenshot(device)
    
            screen = cv2.imread(image_path)
    
            if screen is None:
                print("Failed to read screenshot")
                return None
    
            name_img = screen[434:865, 1124:1462]
    
            raw_name = read_text(name_img)
            name = self.normalize_account_name(raw_name)
    
            print(f"[OCR RAW] {raw_name}")
            print(f"[OCR NORMALIZED] {name}")
    
            if not name:
                return None
    
            return name
    def save_current_account(self, device):
        name = self.read_current_account_name(device)

        if name:
            self.current_account = name
            print(f"[ACCOUNT SAVED] {self.current_account}")

        return self.current_account

    def get_current_account(self):
        """
            Lấy account hiện tại.
            """
        return self.current_account
    def normalize_account_name(self, name: str) -> str:
        """
        Chuẩn hóa tên account OCR.
        """

        if not name:
            return ""

        name = name.strip()

        # bỏ xuống dòng
        name = name.replace("\n", "")

        # bỏ tab
        name = name.replace("\t", "")

        # nhiều khoảng trắng -> 1 khoảng trắng
        name = " ".join(name.split())

        # nếu muốn không phân biệt hoa thường
        name = name.lower()

        return name
    def clear_current_account(self):
        """
        Xóa account hiện tại.
        """
        self.current_account = None