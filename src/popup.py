import pyautogui


def show_confirm_box(message):
    result = pyautogui.confirm(message)
    if result == "OK":
        return True
    return False


def show_alert_box(message):
    pyautogui.alert(text=message, title="Info")


def show_error_box(message):
    pyautogui.alert(text=message, title="Error")
