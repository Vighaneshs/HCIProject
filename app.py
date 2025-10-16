import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import keyboard
import pygetwindow as gw
import pyautogui
import tempfile
import os
from datetime import datetime

# ---------------- CONFIGURATION ---------------- #
DEFAULT_SHORTCUT = "shift+p"
# SAVE_DIR = os.path.join(tempfile.gettempdir(), "screenshots_gui")  # You can change this
SAVE_DIR =os.getcwd()
os.makedirs(SAVE_DIR, exist_ok=True)
# ------------------------------------------------ #

def capture_active_window_screenshot():
    """Capture and save a screenshot of the active window."""
    try:
        win = gw.getActiveWindow()
        if win is None:
            messagebox.showerror("Error", "No active window detected.")
            return None

        left, top, right, bottom = win.left, win.top, win.right, win.bottom
        screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(SAVE_DIR, filename)
        screenshot.save(filepath)
        return filepath
    except Exception as e:
        messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
        return None


class ScreenshotApp:
    def __init__(self, master):
        self.master = master
        master.title("Screenshot Tool")
        master.geometry("500x300")
        master.attributes("-topmost", True)

        self.info_label = tk.Label(master, text=f"Press {DEFAULT_SHORTCUT.upper()} to take a screenshot of the active window.")
        self.info_label.pack(pady=10)

        self.prompt_box = scrolledtext.ScrolledText(master, height=4, wrap=tk.WORD)
        self.prompt_box.insert(tk.END, "Screenshots will be saved in:\n" + SAVE_DIR)
        self.prompt_box.config(state="disabled")
        self.prompt_box.pack(padx=10, pady=10, fill=tk.X)

        self.log_label = tk.Label(master, text="Activity Log:")
        self.log_label.pack(pady=5)

        self.log_box = scrolledtext.ScrolledText(master, height=8, wrap=tk.WORD)
        self.log_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.shortcut_label = tk.Label(master, text="Shortcut:")
        self.shortcut_label.pack(pady=5)
        self.shortcut_entry = tk.Entry(master)
        self.shortcut_entry.insert(0, DEFAULT_SHORTCUT)
        self.shortcut_entry.pack()

        self.set_shortcut_button = tk.Button(master, text="Set Shortcut", command=self.setPshortcut)
        self.set_shortcut_button.pack(pady=5)
        keyboard.add_hotkey(DEFAULT_SHORTCUT, self.on_hotkey_triggered)

    def set_shortcut(self):
        new_shortcut = self.shortcut_entry.get().strip()
        if new_shortcut:
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(new_shortcut, self.on_hotkey_triggered)
            messagebox.showinfo("Shortcut Changed", f"New shortcut: {new_shortcut.upper()}")

    def on_hotkey_triggered(self):
        threading.Thread(target=self.take_screenshot).start()

    def take_screenshot(self):
        filepath = capture_active_window_screenshot()
        if filepath:
            self.log_box.insert(tk.END, f"✅ Screenshot saved: {filepath}\n")
            self.log_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
