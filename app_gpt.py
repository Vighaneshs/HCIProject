
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import keyboard
import pygetwindow as gw
import pyautogui
import tempfile
import base64
import requests
import os
from PIL import Image

# ------------------- CONFIGURATION ------------------- #
API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your key
MODEL = "gpt-4o-mini"  # image-capable model
DEFAULT_PROMPT = "Here is a screenshot of the current application. What should I do next?"
DEFAULT_SHORTCUT = "shift+p"
# ------------------------------------------------------ #

def capture_active_window_screenshot():
    """Capture the screenshot of the currently active window."""
    try:
        win = gw.getActiveWindow()
        if win is None:
            messagebox.showerror("Error", "No active window detected.")
            return None

        # Get window bounding box
        left, top, right, bottom = win.left, win.top, win.right, win.bottom
        screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

        # Save temporary screenshot
        temp_path = os.path.join(tempfile.gettempdir(), "active_window.png")
        screenshot.save(temp_path)
        return temp_path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to capture window: {e}")
        return None


def send_to_chatgpt(image_path, user_prompt):
    """Send the screenshot and text prompt to ChatGPT API and return the response."""
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        headers = {"Authorization": f"Bearer {API_KEY}"}
        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }
            ]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error: {e}"


class ScreenshotApp:
    def __init__(self, master):
        self.master = master
        master.title("Screenshot Assistant")
        master.geometry("600x400")
        master.attributes("-topmost", True)

        self.prompt_label = tk.Label(master, text=f"Press {DEFAULT_SHORTCUT.upper()} to take a screenshot:")
        self.prompt_label.pack(pady=5)

        self.prompt_box = scrolledtext.ScrolledText(master, height=4, wrap=tk.WORD)
        self.prompt_box.insert(tk.END, DEFAULT_PROMPT)
        self.prompt_box.pack(padx=10, pady=5, fill=tk.X)

        self.response_label = tk.Label(master, text="ChatGPT Response:")
        self.response_label.pack(pady=5)

        self.response_box = scrolledtext.ScrolledText(master, height=10, wrap=tk.WORD)
        self.response_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.shortcut_label = tk.Label(master, text="Shortcut:")
        self.shortcut_label.pack(pady=5)
        self.shortcut_entry = tk.Entry(master)
        self.shortcut_entry.insert(0, DEFAULT_SHORTCUT)
        self.shortcut_entry.pack()

        self.set_shortcut_button = tk.Button(master, text="Set Shortcut", command=self.set_shortcut)
        self.set_shortcut_button.pack(pady=5)

        # Register default hotkey
        keyboard.add_hotkey(DEFAULT_SHORTCUT, self.on_hotkey_triggered)

    def set_shortcut(self):
        new_shortcut = self.shortcut_entry.get().strip()
        if new_shortcut:
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(new_shortcut, self.on_hotkey_triggered)
            messagebox.showinfo("Shortcut Changed", f"New shortcut: {new_shortcut.upper()}")

    def on_hotkey_triggered(self):
        threading.Thread(target=self.process_screenshot_and_prompt).start()

    def process_screenshot_and_prompt(self):
        prompt_text = self.prompt_box.get("1.0", tk.END).strip()
        self.response_box.delete("1.0", tk.END)
        self.response_box.insert(tk.END, "⏳ Taking screenshot and contacting ChatGPT...\n")

        image_path = capture_active_window_screenshot()
        if not image_path:
            return

        response = send_to_chatgpt(image_path, prompt_text)
        self.response_box.delete("1.0", tk.END)
        self.response_box.insert(tk.END, response)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
