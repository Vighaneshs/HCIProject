from screenshot import take_active_window_screenshot
from api_client import send_to_backend

def handle_hotkey(ui):
    # Show a status message to the user
    ui.show_message("Capturing screenshot…")
    try:
        # Take screenshot of active window
        filename = take_active_window_screenshot()
        ui.show_message(f"Screenshot saved: {filename}\nSending to LLM…")
        # Send the screenshot to backend
        ok, reply = send_to_backend(filename, task="some_task")
        # Update the UI with the LLM response on success
        ui.show_message(reply if ok else f"Error: {reply}")
    except Exception as e:
        ui.show_message(f"Error: {e}")