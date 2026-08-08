import cv2
import os

def check_pixels(image_path, pixels, tolerance=10):
    image = cv2.imread(image_path)
    if image is None:
        return False

    for x, y, target in pixels:
        if y >= image.shape[0] or x >= image.shape[1]:
            return False
        b, g, r = image[y, x]
        tr, tg, tb = target

        if (
            abs(r - tr) > tolerance or
            abs(g - tg) > tolerance or
            abs(b - tb) > tolerance
        ):
            return False

    return True

def load_image(path):
    if not path or not os.path.exists(path):
        return None
    return cv2.imread(path)


def match_template(screen, template):

    return cv2.matchTemplate(
        screen,
        template,
        cv2.TM_CCOEFF_NORMED
    )


def find_best_match(result):

    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    return max_val, max_loc


def get_center(location, template):

    h, w = template.shape[:2]

    x = location[0] + w // 2
    y = location[1] + h // 2

    return x, y
def find(template_path, screen_path, threshold=0.5):

    screen = load_image(screen_path)
    template = load_image(template_path)

    if screen is None or template is None:
        return None

    result = match_template(screen, template)

    score, location = find_best_match(result)

    print(f"{template_path} : {score:.2f}")
    #da sửa threshold
    if score < threshold:
        return None

    return get_center(location, template)
import cv2

def get_pixel(image_path, x, y):

    image = cv2.imread(image_path)

    b, g, r = image[y, x]

    return (r, g, b)