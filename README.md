# Screenshot GUI Tool

This Python application allows users to capture screenshots of the active window using a configurable keyboard shortcut.  
The program includes a simple graphical user interface (GUI) that remains on top of other windows and maintains an activity log of all screenshots taken.

---

## Features

- Captures screenshots of the active window only.
- Configurable keyboard shortcut (default: Shift + P).
- Graphical user interface that remains always on top.
- Activity log displaying saved screenshot paths.
- Screenshots are automatically saved in the current working directory.

---

## Requirements

The application relies on the following Python libraries:

- `tkinter` (standard library)
- `threading` (standard library)
- `keyboard`
- `pygetwindow`
- `pyautogui`
- `datetime` (standard library)
- `tempfile` (standard library)
- `os` (standard library)
- `scrolledtext` and `messagebox` (included with `tkinter`)

Only the third-party dependencies listed in `requirements.txt` must be installed manually.

---

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
