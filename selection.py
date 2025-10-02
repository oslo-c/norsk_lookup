# Clipboard/selection capture: send Ctrl+C and read clipboard text.

import time
import pyperclip
import keyboard

def copy_selection(delay: float = 0.08) -> str:
    """
    Sends Ctrl+C to copy the active selection and returns the trimmed text.
    Note: For elevated target apps, run this utility as admin.
    """
    prev = None
    try:
        prev = pyperclip.paste()
    except Exception:
        pass

    keyboard.press_and_release("ctrl+c")
    time.sleep(delay)

    try:
        text = pyperclip.paste()
    except Exception:
        text = ""

    # Optional: restore clipboard contents if you want zero side-effects
    # if prev is not None:
    #     try: pyperclip.copy(prev)
    #     except Exception: pass

    return (text or "").strip()
