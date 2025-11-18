"""
Analytics service for Pomodoro Timer application.

This module provides functionality to parse session logs and compute
productivity statistics including sessions, focus time, streaks, and averages.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


# Regex pattern for parsing log lines
# Supports flexible format: timestamp | session_type | status [| duration=X] [| cycle=N] [| tag=TAG]
LOG_LINE_PATTERN = re.compile(
    r'^(?P<timestamp>[^\|]+?)\s*\|\s*'
    r'(?P<session_type>\w+)\s*\|\s*'
    r'(?P<status>\w+)'
    r'(?:\s*\|\s*(?P<extra>.+))?$'
)


@dataclass
class SessionEntry:
    """Represents a parsed session log entry."""
    timestamp: datetime
    session_type: str  # work, short_break, long_break
    status: str  # completed, skipped
    duration_seconds: int = 0
    cycle: Optional[int] = None
    tag: Optional[str] = None


def _parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string, supporting both naive and UTC (Z suffix) formats.
    
    Args:
        timestamp_str: Timestamp string to parse
        
    Returns:
        datetime object or None if parsing fails
    """
    timestamp_str = timestamp_str.strip()
    
    # Try ISO8601 with Z suffix
    if timestamp_str.endswith('Z'):
        try:
            return datetime.fromisoformat(timestamp_str[:-1])
        except ValueError:
            pass
    
    # Try ISO8601 format
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        pass
    
    # Try common datetime formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%f',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None


def _parse_extra_fields(extra_str: str) -> Dict[str, Any]:
    """
    Parse extra fields from log line (duration, cycle, tag).
    
    Args:
        extra_str: String containing extra fields
        
    Returns:
        Dictionary with parsed fields
    """
    result = {}
    
    if not extra_str:
        return result
    
    # Split by | to get individual fields
    parts = [part.strip() for part in extra_str.split('|')]
    
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'duration':
                try:
                    result['duration_seconds'] = int(value)
                except ValueError:
                    pass
            elif key == 'cycle':
                try:
                    result['cycle'] = int(value)
                except ValueError:
                    pass
            elif key == 'tag':
                result['tag'] = value
    
    return result


def parse_log_file(log_path: Path) -> Tuple[List[SessionEntry], int]:
    """
    Parse log file and extract session entries.
    
    Args:
        log_path: Path to log file
        
    Returns:
        Tuple of (list of SessionEntry objects, count of malformed entries)
    """
    entries = []
    malformed_count = 0
    
    if not log_path.exists():
        return entries, malformed_count
    
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            match = LOG_LINE_PATTERN.match(line)
            if not match:
                malformed_count += 1
                continue
            
            # Parse timestamp
            timestamp = _parse_timestamp(match.group('timestamp'))
            if timestamp is None:
                malformed_count += 1
                continue
            
            session_type = match.group('session_type').strip()
            status = match.group('status').strip()
            
            # Parse extra fields if present
            extra_fields = _parse_extra_fields(match.group('extra') or '')
            
            entry = SessionEntry(
                timestamp=timestamp,
                session_type=session_type,
                status=status,
                duration_seconds=extra_fields.get('duration_seconds', 0),
                cycle=extra_fields.get('cycle'),
                tag=extra_fields.get('tag')
            )
            
            entries.append(entry)
    
    return entries, malformed_count


def _compute_consecutive_streak(entries: List[SessionEntry]) -> int:
    """
    Compute consecutive days with at least one completed work session.
    Streak ends at today (inclusive).
    
    Args:
        entries: List of session entries
        
    Returns:
        Number of consecutive days with completed work sessions
    """
    if not entries:
        return 0
    
    # Get completed work sessions only
    work_sessions = [
        e for e in entries 
        if e.session_type == 'work' and e.status == 'completed'
    ]
    
    if not work_sessions:
        return 0
    
    # Get unique dates with completed work sessions
    dates_with_work = set()
    for entry in work_sessions:
        dates_with_work.add(entry.timestamp.date())
    
    # Count consecutive days ending today
    today = datetime.now().date()
    streak = 0
    
    current_date = today
    while current_date in dates_with_work:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak


def compute_stats(entries: List[SessionEntry], malformed_count: int) -> Dict[str, Any]:
    """
    Compute aggregated statistics from session entries.
    
    Args:
        entries: List of parsed session entries
        malformed_count: Count of malformed log entries
        
    Returns:
        Dictionary containing computed statistics
    """
    now = datetime.now()
    today = now.date()
    
    # Determine week boundaries (Monday-Sunday)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Initialize session counts
    session_stats = {
        'work': {'completed': 0, 'skipped': 0, 'total_duration_seconds': 0},
        'short_break': {'completed': 0, 'skipped': 0, 'total_duration_seconds': 0},
        'long_break': {'completed': 0, 'skipped': 0, 'total_duration_seconds': 0},
    }
    
    # Initialize focus metrics
    today_work_sessions = 0
    today_focus_seconds = 0
    week_focus_seconds = 0
    
    # Process entries
    for entry in entries:
        entry_date = entry.timestamp.date()
        
        # Update session stats
        if entry.session_type in session_stats:
            session_stats[entry.session_type][entry.status] = \
                session_stats[entry.session_type].get(entry.status, 0) + 1
            
            if entry.status == 'completed':
                session_stats[entry.session_type]['total_duration_seconds'] += entry.duration_seconds
        
        # Update focus metrics (work sessions only)
        if entry.session_type == 'work':
            if entry_date == today and entry.status == 'completed':
                today_work_sessions += 1
                today_focus_seconds += entry.duration_seconds
            
            if week_start <= entry_date <= week_end and entry.status == 'completed':
                week_focus_seconds += entry.duration_seconds
    
    # Calculate completion ratio
    total_sessions = sum(
        stats['completed'] + stats['skipped']
        for stats in session_stats.values()
    )
    completed_sessions = sum(
        stats['completed']
        for stats in session_stats.values()
    )
    completion_ratio = completed_sessions / total_sessions if total_sessions > 0 else 0.0
    
    # Calculate average work session duration
    completed_work = session_stats['work']['completed']
    total_work_duration = session_stats['work']['total_duration_seconds']
    avg_work_duration = total_work_duration / completed_work if completed_work > 0 else 0
    
    # Calculate estimated full cycles (4 work sessions = 1 cycle)
    estimated_cycles = completed_work // 4
    
    # Calculate streak
    streak = _compute_consecutive_streak(entries)
    
    # Build result
    result = {
        'generated_at': now.isoformat(),
        'log_entries': len(entries),
        'malformed_entries': malformed_count,
        'date_scope': {
            'today': today.isoformat(),
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
        },
        'sessions': {
            session_type: {
                'completed': stats['completed'],
                'skipped': stats['skipped'],
                'total_duration_seconds': stats['total_duration_seconds'],
            }
            for session_type, stats in session_stats.items()
        },
        'focus': {
            'today_work_sessions_completed': today_work_sessions,
            'today_focus_minutes': today_focus_seconds / 60,
            'week_focus_minutes': week_focus_seconds / 60,
            'completion_ratio': completion_ratio,
        },
        'streaks': {
            'consecutive_focus_days': streak,
        },
        'averages': {
            'avg_work_session_duration_seconds': avg_work_duration,
        },
        'cycles': {
            'estimated_full_cycles_completed': estimated_cycles,
        },
    }
    
    return result


def generate_stats(log_path: Path) -> Dict[str, Any]:
    """
    Convenience function to generate statistics from log file.
    
    Args:
        log_path: Path to log file
        
    Returns:
        Dictionary containing computed statistics
    """
    entries, malformed_count = parse_log_file(log_path)
    return compute_stats(entries, malformed_count)
