import pyautogui


def show_confirm_box(message):
    result = pyautogui.confirm(message)
    if result == "OK":
        return True
    return False


def show_alert_box(message):
    pyautogui.alert(message)
