import subprocess as s
import time
import os
def get_temp_path(device):
    os.makedirs("temp", exist_ok=True)
    return f"temp/{device}.png"
def tap(device, x, y):

    s.run([
        "adb",
        "-s",
        device,
        "shell",
        "input",
        "tap",
        str(x),
        str(y)
    ])
def swipe(device,x1, y1, x2, y2, duration=200):

    s.run([
        "adb",
        "-s",
        device,
        "shell",
        "input",
        "swipe",
        str(x1),
        str(y1),
        str(x2),
        str(y2),
        str(duration)
    ])
def input_text(device,text):

    if device is None:
        return

    s.run([
        "adb",
        "-s",
        device,
        "shell",
        "input",
        "text",
        text
    ])
def screenshot(device, name=None):

    if name:
        os.makedirs("temp", exist_ok=True)
        final_path = f"temp/{device}_{name}.png"
    else:
        final_path = get_temp_path(device)

    tmp_path = f"{final_path}.tmp"

    try:
        with open(tmp_path, "wb") as image:
            s.run(
                [
                    "adb",
                    "-s",
                    device,
                    "exec-out",
                    "screencap",
                    "-p"
                ],
                stdout=image
            )
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            os.replace(tmp_path, final_path)
    except Exception as e:
        print("Screenshot error:", e)

    return final_path
def home(device):

    

    if device is None:
        return

    s.run([
        "adb",
        "-s",
        device,
        "shell",
        "input",
        "keyevent",
        "3"
    ])
def interruptible_sleep(seconds, stop_check=None):
    end = time.time() + seconds

    while time.time() < end:
        if stop_check and stop_check():
            return False
        time.sleep(0.05)

    return True
def deploy(device, x, y, count, delay=0.1, stop_check=None):

    if count ==1:
        tap(device,x, y)
    else:
        for _ in range(2):
            if count == 2:
                tap(device,185,304)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,291,382)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,412,479)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,960,606)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,1200,425)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,1313,351)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,1293,135)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,254,144)
            elif count == 3:
                tap(device,1375,220)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,1440,280)
                if not interruptible_sleep(delay, stop_check):
                    return False
                tap(device,1400,320)