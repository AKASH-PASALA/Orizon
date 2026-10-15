import time
import os
from pathlib import Path

import pyautogui


# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


def type_text(text):
    if not text.strip():
        return "Boss, please tell me what to type."

    pyautogui.write(text, interval=0.03)
    return "Done, Boss. I've typed your text."


def press_key(key):
    allowed_keys = {
        "enter": "enter",
        "escape": "esc",
        "tab": "tab",
        "space": "space",
        "backspace": "backspace",
        "delete": "delete",
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "home": "home",
        "end": "end"
    }

    key = key.lower().strip()

    if key not in allowed_keys:
        return "Boss, that key isn't supported yet."

    pyautogui.press(allowed_keys[key])
    return f"Done, Boss. I pressed {key}."


def save_document():
    pyautogui.hotkey("ctrl", "s")
    return "Save shortcut pressed, Boss."


def switch_window():
    pyautogui.hotkey("alt", "tab")
    return "Switching windows, Boss."


def copy_selected():
    pyautogui.hotkey("ctrl", "c")
    return "Copy shortcut pressed, Boss."


def paste_content():
    pyautogui.hotkey("ctrl", "v")
    return "Paste shortcut pressed, Boss."


def take_screenshot():
    folder = Path.home() / "OrizonFiles" / "Screenshots"
    folder.mkdir(parents=True, exist_ok=True)

    filename = time.strftime("screenshot_%Y%m%d_%H%M%S.png")
    filepath = folder / filename

    pyautogui.screenshot().save(filepath)

    return f"Boss, screenshot saved at {filepath}."


if __name__ == "__main__":
    print("Computer control module loaded.")
    print("Move your mouse to the top-left corner to trigger the PyAutoGUI failsafe.")