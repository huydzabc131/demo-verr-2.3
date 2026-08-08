import os
import time
from config import ASSET_PATH,DEFAULT_THRESHOLD
from core.adb import screenshot, tap
from core.vision import find
from core.adb import deploy

def click(device,template_name, threshold=DEFAULT_THRESHOLD):

    screen_path = screenshot(device)
    template = os.path.join(
        ASSET_PATH,
        f"{template_name}.png"
    )

    position = find(template, screen_path, threshold)

    if position is None:
        return False

    tap(device,*position)

    return True


def wait_image(
    device,
    template_name,
    timeout=10,
    threshold=DEFAULT_THRESHOLD,
    stop_check=None
):
    template = os.path.join(
        ASSET_PATH,
        f"{template_name}.png"
    )

    start = time.time()

    while time.time() - start < timeout:

        if stop_check and stop_check():
            return None

        screen_path = screenshot(device)

        position = find(
            template,
            screen_path,
            threshold
        )

        if position is not None:
            return position

        time.sleep(0.3)

    return None


def click_when_found(
    device,
    template_name,
    timeout=10,
    threshold=DEFAULT_THRESHOLD,
    stop_check=None
):

    position = wait_image(
        device,
        template_name,
        timeout,
        threshold,
        stop_check
    )

    if position is None:
        return False

    tap(device, *position)

    return True
def deploy_hero(device,name, x, y):

    if click(device,name):
        tap(device,x, y)
def deploy_spell(device,name, x, y, count=1):

    if click(device,name):

        deploy(device,x, y, count)
import os
from config import ASSET_PATH, DEFAULT_THRESHOLD
from core.adb import screenshot
from core.vision import find

def exists(device,template_name, threshold=DEFAULT_THRESHOLD):

    screen_path = screenshot(device)

    template = os.path.join(
        ASSET_PATH,
        f"{template_name}.png"
    )

    position = find(template, screen_path, threshold)

    return position is not None