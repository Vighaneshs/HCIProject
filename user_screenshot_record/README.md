# Screen Capture Event Logger

This tool captures screenshots along with mouse and keyboard events, organizing them by user and task IDs. It's designed to track user interactions with detailed event logging.

## Setup and Configuration

### Config File (`config.json`)
Before running the tool, edit the `config.json` file to set up your user and task information:

```json
{
    "user_id": "your_user_id",
    "task_id": "your_task_id"
}
```

- `user_id`: Unique identifier for the user performing the task
- `task_id`: Unique identifier for the specific task being performed

Example configuration:
```json
{
    "user_id": "user123",
    "task_id": "task_A"
}
```

### Directory Structure

The tool organizes captured data into two directories:

- `screenshots/`: Contains all captured screenshot images
- `records/`: Contains event log JSON files

### File Naming Convention

- Screenshots: `{user_id}_{task_id}_{counter}_{timestamp}.png`
- Event logs: `{user_id}_{task_id}_events.json`

## Event Tracking

The tool records the following information for each event:

1. Mouse Clicks:
   - Timestamp
   - Click position (x, y coordinates)
   - Mouse button used
   - Associated screenshot filename

2. Keyboard Presses:
   - Timestamp
   - Key pressed
   - Mouse position at time of keypress
   - Associated screenshot filename

### Sample Event Log Structure
```json
{
    "timestamp": "2025-10-29T14:30:45.123456",
    "event_type": "mouse_click",
    "details": {
        "button": "Button.left",
        "position": {
            "x": 500,
            "y": 300
        }
    },
    "screenshot": "user123_task_A_1_20251029_143045.png"
}
```

## Usage

1. Edit `config.json` with appropriate user_id and task_id
2. Run the script:
   ```bash
   python screen_capture_event.py
   ```
3. Use your computer normally - the tool will capture:
   - Screenshots on every mouse click
   - Screenshots on every keyboard press
   - Cursor position for all events

4. To exit:
   - Press ESC key
   - Or use Ctrl+C

## Data Analysis

All captured data is organized by user_id and task_id, making it easy to:
- Track specific user sessions
- Analyze task-specific interactions
- Correlate events with screenshots
- Compare different users or tasks

The JSON records provide a detailed timeline of all interactions, each linked to its corresponding screenshot for comprehensive analysis.