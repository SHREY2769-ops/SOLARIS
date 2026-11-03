"""Screen: takes a screenshot ONLY when you ask a question about your screen."""
import base64
import ctypes
import io
import os
import time
from PIL import ImageGrab
import config

_user32 = None
if os.name == "nt":
    _user32 = ctypes.windll.user32
    try:
        _user32.SetProcessDPIAware()   # so screenshots aren't cropped on scaled screens
    except Exception:
        pass


def capture_b64(window_title=None, max_width=1600):
    hwnd = None
    if _user32 and window_title and config.HIDE_ON_CAPTURE:
        hwnd = _user32.FindWindowW(None, window_title)
        if hwnd:
            _user32.ShowWindow(hwnd, 6)    # minimise Jarvis so he isn't in the picture
            time.sleep(0.7)
    try:
        img = ImageGrab.grab().convert("RGB")
    finally:
        if hwnd:
            _user32.ShowWindow(hwnd, 9)    # bring him back
    if img.width > max_width:
        img = img.resize((max_width, round(img.height * max_width / img.width)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()
