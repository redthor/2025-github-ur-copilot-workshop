# Pomodoro Timer Web App

A simple and elegant Pomodoro Timer web application built with Flask and vanilla JavaScript. This app helps you stay focused and productive using the Pomodoro Technique.

## Features

- **Timer Functionality**: 25-minute work sessions with 5-minute short breaks and 15-minute long breaks
- **Session Tracking**: Visual progress indicator showing completed sessions
- **Customizable Settings**: Adjust work and break durations to your preference
- **Session Logging**: Automatic logging of completed and skipped sessions
- **Responsive Design**: Works on desktop and mobile devices
- **Browser Notifications**: Get notified when sessions complete

## Pomodoro Technique

The Pomodoro Technique uses a timer to break work into intervals:
1. 25 minutes of focused work
2. 5-minute short break
3. Repeat 4 times
4. Take a 15-minute long break after 4 sessions

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pomodoro_app
   ```

2. **Create virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install Flask
   ```

## Running the Application

1. **Activate virtual environment** (if not already activated):
   ```bash
   source .venv/bin/activate
   ```

2. **Start the Flask application**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

1. **Start a Session**: Click the "Start" button to begin a 25-minute work session
2. **Pause/Resume**: Click "Start" again to pause, and once more to resume
3. **Reset**: Click "Reset" to restart the current session
4. **Skip**: Click "Skip" to move to the next session (break or work)
5. **Settings**: Click "Settings" to customize session durations
6. **Progress**: Watch the dots at the bottom to track your progress through the 4-session cycle

## Project Structure

```
pomodoro_app/
├── app.py                  # Flask backend server
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── style.css          # CSS styling
│   └── timer.js           # JavaScript timer logic
├── pomodoro_log.txt       # Session log file (created automatically)
└── README.md              # This file
```

## API Endpoints

- `GET /` - Serves the main timer page
- `POST /log` - Logs session events (completed/skipped)
- `GET /history` - Returns session history (optional)
- `GET /stats` - Returns aggregated productivity analytics

## Session Logging

The app automatically logs all session events to `pomodoro_log.txt` with the following format:
```
timestamp | session_type | action | session_number
```

Example:
```
2024-01-15 14:30:00 | work | completed | session_1
2024-01-15 14:55:00 | short_break | completed | session_1
```

## New Analytics Endpoint

The `/stats` endpoint provides aggregated productivity metrics based on your session log history.

### Sample Response

```json
{
  "generated_at": "2025-11-18T22:41:20.058828",
  "log_entries": 6,
  "malformed_entries": 0,
  "date_scope": {
    "today": "2025-11-18",
    "week_start": "2025-11-17",
    "week_end": "2025-11-23"
  },
  "sessions": {
    "work": {
      "completed": 2,
      "skipped": 2,
      "total_duration_seconds": 0
    },
    "short_break": {
      "completed": 2,
      "skipped": 0,
      "total_duration_seconds": 0
    },
    "long_break": {
      "completed": 0,
      "skipped": 0,
      "total_duration_seconds": 0
    }
  },
  "focus": {
    "today_work_sessions_completed": 0,
    "today_focus_minutes": 0.0,
    "week_focus_minutes": 0.0,
    "completion_ratio": 0.67
  },
  "streaks": {
    "consecutive_focus_days": 0
  },
  "averages": {
    "avg_work_session_duration_seconds": 0.0
  },
  "cycles": {
    "estimated_full_cycles_completed": 0
  }
}
```

### Metrics Explained

- **log_entries**: Number of successfully parsed log lines
- **malformed_entries**: Count of unparseable log lines (gracefully skipped)
- **date_scope**: Current date and week boundaries (Monday-Sunday)
- **sessions**: Per-type breakdown of completed/skipped sessions and total duration
- **focus**: 
  - `today_work_sessions_completed`: Work sessions completed today
  - `today_focus_minutes`: Total focused work time today
  - `week_focus_minutes`: Total focused work time this week
  - `completion_ratio`: Ratio of completed to total sessions (all types)
- **streaks**:
  - `consecutive_focus_days`: Days in a row (ending today) with ≥1 completed work session
- **averages**:
  - `avg_work_session_duration_seconds`: Average duration of completed work sessions
- **cycles**:
  - `estimated_full_cycles_completed`: Number of full Pomodoro cycles (4 work sessions = 1 cycle)


## Customization

### Settings
- **Work Duration**: Default 25 minutes (adjustable 1-60 minutes)
- **Short Break**: Default 5 minutes (adjustable 1-30 minutes)  
- **Long Break**: Default 15 minutes (adjustable 1-60 minutes)

Settings are saved in your browser's localStorage and persist between sessions.

### Browser Notifications
The app requests permission for browser notifications to alert you when sessions complete. You can enable/disable this in your browser settings.

## Development

### Adding Features
- Modify `app.py` for backend changes
- Edit `timer.js` for timer logic updates
- Update `style.css` for styling changes
- Modify `index.html` for UI structure changes

### Testing
Run the Flask app in debug mode (default) to see detailed error messages and automatic reloading during development.

## Browser Support
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## License
MIT License - feel free to use and modify as needed.