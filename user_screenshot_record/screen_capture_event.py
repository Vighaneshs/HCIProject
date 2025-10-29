import json
from pynput import mouse, keyboard
import pyautogui
import os
import signal
import sys
from datetime import datetime
from PIL import Image, ImageDraw

class ScreenCaptureEvent:
    def __init__(self, config_path='config.json'):
        self.screenshot_counter = 0
        self.config = self.load_config(config_path)
        self.user_id = self.config.get('user_id', 'default_user')
        self.task_id = self.config.get('task_id', 'default_task')
        self.output_dir = 'screenshots'
        self.records_dir = 'records'
        self.events = []
        
        # Create necessary directories if they don't exist
        for directory in [self.output_dir, self.records_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
            
        # Initialize events file
        self.events_file = os.path.join(self.records_dir, f"{self.user_id}_{self.task_id}_events.json")
        self.load_existing_events()

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config if it doesn't exist
            default_config = {
                'user_id': 'default_user',
                'task_id': 'default_task'
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def load_existing_events(self):
        try:
            with open(self.events_file, 'r') as f:
                self.events = json.load(f)
        except FileNotFoundError:
            self.events = []
            
    def save_events(self):
        with open(self.events_file, 'w') as f:
            json.dump(self.events, f, indent=4)
            
    def add_event(self, event_type, details, screenshot_filename):
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'screenshot': screenshot_filename
        }
        self.events.append(event)
        self.save_events()

    def capture_screenshot(self, x=None, y=None, event_type=None, event_details=None):
        self.screenshot_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.user_id}_{self.task_id}_{self.screenshot_counter}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        
        # If mouse position is provided, draw cursor
        if x is not None and y is not None:
            # Convert to PIL Image if it's not already
            if not isinstance(screenshot, Image.Image):
                screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
            
            # Get the actual screen size
            screen_width, screen_height = pyautogui.size()
            
            # Scale the coordinates to match the screenshot dimensions
            scaled_x = int((x / screen_width) * screenshot.width)
            scaled_y = int((y / screen_height) * screenshot.height)
            
            # Create a drawing object
            draw = ImageDraw.Draw(screenshot)
            
            # Draw a small circle at cursor position
            cursor_radius = 10
            draw.ellipse([scaled_x - cursor_radius, scaled_y - cursor_radius, 
                         scaled_x + cursor_radius, scaled_y + cursor_radius], 
                         fill='red', outline='white')
        
        # Save the screenshot
        screenshot.save(filepath)
        print(f"Screenshot saved: {filepath}")
        
        # Record the event if provided
        if event_type and event_details:
            self.add_event(event_type, event_details, filename)

    def on_click(self, x, y, button, pressed):
        if pressed:  # Only capture on mouse press, not release
            # Get current mouse position
            event_details = {
                'button': str(button),
                'position': {'x': x, 'y': y}
            }
            self.capture_screenshot(x, y, 'mouse_click', event_details)

    def on_press(self, key):
        # Get current mouse position
        x, y = pyautogui.position()
        
        # Create event details
        try:
            key_char = key.char  # For alphanumeric keys
        except AttributeError:
            key_char = str(key)  # For special keys
            
        event_details = {
            'key': key_char,
            'position': {'x': x, 'y': y}
        }
        
        self.capture_screenshot(x, y, 'key_press', event_details)
        
        # Check for exit condition (ESC key)
        if key == keyboard.Key.esc:
            return False

    def cleanup(self):
        print("\nStopping screen capture...")
        self.save_events()  # Ensure all events are saved
        sys.exit(0)

    def signal_handler(self, signum, frame):
        self.cleanup()

    def start(self):
        # Set up signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Start listening to mouse and keyboard events
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        mouse_listener = mouse.Listener(on_click=self.on_click)
        
        print(f"Starting screen capture for user: {self.user_id}")
        print("Press ESC to exit or use Ctrl+C")
        
        try:
            # Start both listeners
            keyboard_listener.start()
            mouse_listener.start()
            
            # Keep the main thread running
            keyboard_listener.join()
            mouse_listener.stop()
        except KeyboardInterrupt:
            self.cleanup()
        finally:
            # Ensure listeners are stopped
            keyboard_listener.stop()
            mouse_listener.stop()

if __name__ == "__main__":
    screen_capture = ScreenCaptureEvent()
    screen_capture.start()
