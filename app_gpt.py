import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import keyboard
import json
import pywinctl as gw
import pyautogui
import tempfile
import base64
import requests
import os
from PIL import Image
import time
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ------------------- CONFIGURATION ------------------- #
MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
DEFAULT_TASK = "I want to open a new file in vscode"
DEFAULT_PROMPT = "I will provide a screen shot of the app, make sure you tell me only the next step to take and nothing else, to execute the task succesfully in the future steps."
DEFAULT_SHORTCUT = "shift"
LOG_FILE = "activity_log.txt"
# ------------------------------------------------------ #

def log_event(event_data):
    """Append event data with timestamp to a single persistent log file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOGGER ERROR] {e}")


def capture_active_window_screenshot():
    """Capture the screenshot of the currently active window."""
    try:
        win = gw.getActiveWindow()
        if win is None:
            messagebox.showerror("Error", "No active window detected.")
            return None

        left, top, right, bottom = win.left, win.top, win.right, win.bottom
        screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
        temp_path = os.path.join(tempfile.gettempdir(), "active_window.png")
        screenshot.save(temp_path)

        # Log screenshot event
        log_event({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "screenshot_taken",
            "screenshot_path": temp_path
        })
        return temp_path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to capture window: {e}")
        return None


def send_to_LLM(image_path, user_prompt):
    """Send the screenshot and text prompt to OpenRouter API and return the response."""
    send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_event({
        "timestamp": send_time,
        "event": "request_sent",
        "model": MODEL,
        "prompt": user_prompt
    })

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        start = time.time()
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            },
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }
            ]
        )
        response = completion.choices[0].message.content
        end = time.time()

        log_event({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "response_received",
            "response_time_sec": round(end - start, 2),
            "response": response
        })
        return response
    except Exception as e:
        log_event({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "error",
            "error_message": str(e)
        })
        return f"❌ Error: {e}"


class ScreenshotApp:
    step_number = 1

    def __init__(self, master):
        self.master = master
        master.title("Screenshot Assistant")
        master.geometry("800x640")
        master.attributes("-topmost", True)

        self.prompt_label = tk.Label(master, text=f"Press {DEFAULT_SHORTCUT.upper()} to take a screenshot:")
        self.prompt_label.pack(pady=5)

        self.task_label = tk.Label(master, text="Task:")
        self.task_label.pack(pady=5)

        self.task_box = scrolledtext.ScrolledText(master, height=4, wrap=tk.WORD)
        self.task_box.insert(tk.END, DEFAULT_TASK)
        self.task_box.pack(padx=10, pady=5, fill=tk.X)

        self.prompt_label = tk.Label(master, text="Instructions to LLM:")
        self.prompt_label.pack(pady=5)

        self.prompt_box = scrolledtext.ScrolledText(master, height=4, wrap=tk.WORD)
        self.prompt_box.insert(tk.END, DEFAULT_PROMPT)
        self.prompt_box.pack(padx=10, pady=5, fill=tk.X)

        self.response_label = tk.Label(master, text="LLM Response:")
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

        self.shortcut_label = tk.Label(master, text="Model:")
        self.shortcut_label.pack(pady=5)
        self.shortcut_entry = tk.Entry(master)
        self.shortcut_entry.insert(0, MODEL)
        self.shortcut_entry.pack()

        self.set_shortcut_button = tk.Button(master, text="Set Model", command=self.set_model)
        self.set_shortcut_button.pack(pady=5)

        keyboard.add_hotkey(DEFAULT_SHORTCUT, self.on_hotkey_triggered)

    def set_shortcut(self):
        new_shortcut = self.shortcut_entry.get().strip()
        if new_shortcut:
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(new_shortcut, self.on_hotkey_triggered)
            messagebox.showinfo("Shortcut Changed", f"New shortcut: {new_shortcut.upper()}")

    def set_model(self):
        global MODEL
        MODEL = self.shortcut_entry.get().strip()

    def on_hotkey_triggered(self):
        threading.Thread(target=self.process_screenshot_and_prompt).start()

    def process_screenshot_and_prompt(self):
        task = self.task_box.get("1.0", tk.END).strip()
        prompt_text = task + ". " + self.prompt_box.get("1.0", tk.END).strip()

        self.response_box.delete("1.0", tk.END)
        self.response_box.insert(tk.END, "⏳ Taking screenshot and contacting OpenRouter...\n")

        image_path = capture_active_window_screenshot()
        if not image_path:
            return

        response = send_to_LLM(image_path, prompt_text)

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": task,
            "step_number": self.step_number,
            "model": MODEL,
            "response": response
        }

        # Save conversation to JSON file
        json_file = "conversation_history.json"
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    conversations = json.load(f)
            else:
                conversations = []

            conversations.append(data)
            with open(json_file, 'w') as f:
                json.dump(conversations, f, indent=4)

            # Log interaction summary
            log_event({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event": "interaction_summary",
                "step_number": self.step_number,
                "task": task,
                "model": MODEL,
                "response": response
            })
        except Exception as e:
            print(f"Error saving to JSON: {e}")

        self.step_number += 1
        self.response_box.delete("1.0", tk.END)
        self.response_box.insert(tk.END, response)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
