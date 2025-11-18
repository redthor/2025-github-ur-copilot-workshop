# Pomodoro Timer API Documentation

This document provides comprehensive API reference for the Pomodoro Timer web application.

## Base URL

When running locally:
```
http://localhost:5000
```

## Endpoints

### 1. GET /

Serves the main Pomodoro Timer web application interface.

**Response:**
- Returns HTML page with the timer interface

**Example:**
```bash
curl http://localhost:5000/
```

---

### 2. POST /log

Logs a Pomodoro session event (completion or skip).

**Request Body:**
```json
{
  "session_type": "work",
  "action": "completed",
  "session_number": 1
}
```

**Parameters:**
- `session_type` (string, optional): Type of session. Default: `"work"`
  - Valid values: `"work"`, `"short_break"`, `"long_break"`
- `action` (string, optional): Action taken. Default: `"completed"`
  - Valid values: `"completed"`, `"skipped"`
- `session_number` (integer, optional): Session number in the cycle. Default: `1`

**Response (Success - 200):**
```json
{
  "status": "success",
  "message": "Session logged successfully"
}
```

**Response (Error - 500):**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/log \
  -H "Content-Type: application/json" \
  -d '{
    "session_type": "work",
    "action": "completed",
    "session_number": 1
  }'
```

**Log File Format:**

Sessions are appended to `pomodoro_log.txt` in the format:
```
timestamp | session_type | action | session_number
```

Example:
```
2025-11-18 14:30:00 | work | completed | session_1
2025-11-18 14:55:00 | short_break | completed | session_1
2025-11-18 15:00:00 | work | skipped | session_2
```

---

### 3. GET /history

Retrieves the raw session history from the log file.

**Response (Success - 200):**
```json
{
  "sessions": [
    {
      "timestamp": "2025-11-18 14:30:00",
      "session_type": "work",
      "action": "completed",
      "session_number": "session_1"
    },
    {
      "timestamp": "2025-11-18 14:55:00",
      "session_type": "short_break",
      "action": "completed",
      "session_number": "session_1"
    }
  ]
}
```

**Response (Error - 500):**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Example:**
```bash
curl http://localhost:5000/history
```

**Notes:**
- Returns empty array if log file doesn't exist
- Malformed log entries are silently skipped
- Only entries with exactly 4 pipe-separated fields are included

---

### 4. GET /stats

Returns aggregated productivity analytics based on session log history.

**Response (Success - 200):**
```json
{
  "generated_at": "2025-11-18T22:41:20.058828",
  "log_entries": 12,
  "malformed_entries": 0,
  "date_scope": {
    "today": "2025-11-18",
    "week_start": "2025-11-17",
    "week_end": "2025-11-23"
  },
  "sessions": {
    "work": {
      "completed": 8,
      "skipped": 1,
      "total_duration_seconds": 12000
    },
    "short_break": {
      "completed": 6,
      "skipped": 0,
      "total_duration_seconds": 1800
    },
    "long_break": {
      "completed": 1,
      "skipped": 0,
      "total_duration_seconds": 900
    }
  },
  "focus": {
    "today_work_sessions_completed": 4,
    "today_focus_minutes": 100.0,
    "week_focus_minutes": 200.0,
    "completion_ratio": 0.94
  },
  "streaks": {
    "consecutive_focus_days": 3
  },
  "averages": {
    "avg_work_session_duration_seconds": 1500.0
  },
  "cycles": {
    "estimated_full_cycles_completed": 2
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `generated_at` | string (ISO8601) | Timestamp when stats were generated |
| `log_entries` | integer | Number of successfully parsed log lines |
| `malformed_entries` | integer | Number of unparseable log lines (gracefully skipped) |
| `date_scope.today` | string (ISO date) | Current date |
| `date_scope.week_start` | string (ISO date) | Start of current week (Monday) |
| `date_scope.week_end` | string (ISO date) | End of current week (Sunday) |
| `sessions.{type}.completed` | integer | Count of completed sessions of this type |
| `sessions.{type}.skipped` | integer | Count of skipped sessions of this type |
| `sessions.{type}.total_duration_seconds` | integer | Total duration of completed sessions in seconds |
| `focus.today_work_sessions_completed` | integer | Work sessions completed today |
| `focus.today_focus_minutes` | float | Total focused work time today (minutes) |
| `focus.week_focus_minutes` | float | Total focused work time this week (minutes) |
| `focus.completion_ratio` | float | Ratio of completed to total sessions (0.0-1.0) |
| `streaks.consecutive_focus_days` | integer | Consecutive days (ending today) with ≥1 completed work session |
| `averages.avg_work_session_duration_seconds` | float | Average duration of completed work sessions |
| `cycles.estimated_full_cycles_completed` | integer | Number of full Pomodoro cycles (4 work sessions = 1 cycle) |

**Response (Error - 500):**
```json
{
  "status": "error",
  "error_code": "STATS_COMPUTE_FAILED",
  "message": "Error description"
}
```

**Example:**
```bash
curl http://localhost:5000/stats
```

**Notes:**
- Stats are computed in real-time from the log file
- Empty log file returns zeros for all metrics
- Week boundaries are Monday-Sunday based on current UTC date
- Streak calculation requires at least one completed work session per day
- Only completed work sessions contribute to focus metrics

---

## Extended Log Format (Future)

The analytics service supports an extended log format with optional fields for future enhancements:

```
timestamp | session_type | status | duration=SECONDS | cycle=N | tag=TAG
```

**Optional Fields:**
- `duration=SECONDS`: Session duration in seconds
- `cycle=N`: Cycle number (integer)
- `tag=TAG`: Custom tag for categorization (reserved for future use)

**Example:**
```
2025-11-18T14:30:00Z | work | completed | duration=1500 | cycle=1 | tag=coding
```

**Backward Compatibility:**
- Old format logs (without optional fields) are fully supported
- Parser gracefully handles missing fields with sensible defaults
- Malformed entries are counted but don't break stats computation

---

## Future Enhancements

Planned features that are not yet implemented:

1. **Caching**: Stats caching to avoid full file reparse on each request
2. **Database Backend**: Alternative to file-based logging
3. **Tag-Based Analytics**: Aggregate stats by custom tags
4. **Query Parameters**: `/stats?scope=week` or `/stats?scope=month` for scoped analytics
5. **User Authentication**: Multi-user support with isolated logs
6. **Export**: Download stats as CSV/JSON
7. **Visualizations**: Chart endpoints returning SVG/PNG graphics

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (malformed JSON)
- `500`: Internal server error

Error responses include:
```json
{
  "status": "error",
  "message": "Human-readable error description"
}
```

For the `/stats` endpoint specifically:
```json
{
  "status": "error",
  "error_code": "STATS_COMPUTE_FAILED",
  "message": "Detailed error message"
}
```

---

## Development and Testing

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest test_stats.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Starting the Development Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start Flask development server
python app.py
```

The server will start on `http://localhost:5000` by default.

---

## Production Deployment

For production deployment, use a production WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Environment variables:
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to `development` for debug mode

---

## Version History

### v1.1 (Current)
- Added `/stats` endpoint for analytics
- Introduced `analytics_service.py` module
- Extended log format support (backward compatible)
- Comprehensive test coverage

### v1.0
- Initial release
- Basic timer functionality
- `/log` and `/history` endpoints
