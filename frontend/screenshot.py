import pyautogui
import pygetwindow as gw
from datetime import datetime
import os

def take_active_window_screenshot() -> str:
    """Capture screenshot of the currently active window."""
    # Get the active window
    window = gw.getActiveWindow()
    if window is None:
        print("No active window detected.")
        return

    # Get window geometry
    left, top, width, height = window.left, window.top, window.width, window.height

    # Take screenshot of that region
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    # Make output folder
    os.makedirs("screenshots", exist_ok=True)

    # Save screenshot with timestamp and window title
    safe_title = "".join(c for c in window.title if c.isalnum() or c in (' ', '_')).rstrip()
    filename = f"screenshots/{safe_title}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    screenshot.save(filename)
    return filename