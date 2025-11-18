"""
Unit tests for Analytics Service and /stats endpoint.
Tests parsing, computation, streak calculation, and API responses.
"""
import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from analytics_service import (
    parse_log_file,
    compute_stats,
    generate_stats,
    _parse_timestamp,
    _compute_consecutive_streak,
    SessionEntry
)
from app import app


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        temp_file_path = tmp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestParseTimestamp:
    """Tests for timestamp parsing"""
    
    def test_parse_iso_with_z_suffix(self):
        """Test parsing ISO8601 timestamp with Z suffix"""
        ts = _parse_timestamp('2025-11-14T11:48:34Z')
        assert ts is not None
        assert ts.year == 2025
        assert ts.month == 11
        assert ts.day == 14
    
    def test_parse_standard_format(self):
        """Test parsing standard datetime format"""
        ts = _parse_timestamp('2025-11-14 11:48:34')
        assert ts is not None
        assert ts.year == 2025
        assert ts.month == 11
        assert ts.day == 14
        assert ts.hour == 11
        assert ts.minute == 48
        assert ts.second == 34
    
    def test_parse_iso_format(self):
        """Test parsing ISO format without Z"""
        ts = _parse_timestamp('2025-11-14T11:48:34')
        assert ts is not None
        assert ts.year == 2025
    
    def test_parse_invalid_timestamp(self):
        """Test parsing invalid timestamp returns None"""
        ts = _parse_timestamp('invalid-timestamp')
        assert ts is None


class TestParseLogFile:
    """Tests for log file parsing"""
    
    def test_parse_empty_log(self, temp_log_file):
        """Test parsing empty log file"""
        Path(temp_log_file).write_text('')
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 0
        assert malformed == 0
    
    def test_parse_nonexistent_log(self):
        """Test parsing non-existent log file"""
        entries, malformed = parse_log_file(Path('/tmp/nonexistent_log_file_xyz.txt'))
        
        assert len(entries) == 0
        assert malformed == 0
    
    def test_parse_basic_entries(self, temp_log_file):
        """Test parsing basic log entries"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | session_1\n'
            '2025-11-14 11:48:35 | short_break | completed | session_1\n'
            '2025-11-14 11:48:36 | work | skipped | session_2\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 3
        assert malformed == 0
        assert entries[0].session_type == 'work'
        assert entries[0].status == 'completed'
        assert entries[1].session_type == 'short_break'
        assert entries[2].status == 'skipped'
    
    def test_parse_with_duration(self, temp_log_file):
        """Test parsing entries with duration field"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | duration=1500\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 1
        assert malformed == 0
        assert entries[0].duration_seconds == 1500
    
    def test_parse_with_cycle(self, temp_log_file):
        """Test parsing entries with cycle field"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | cycle=3\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 1
        assert entries[0].cycle == 3
    
    def test_parse_with_tag(self, temp_log_file):
        """Test parsing entries with tag field"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | tag=coding\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 1
        assert entries[0].tag == 'coding'
    
    def test_parse_with_all_fields(self, temp_log_file):
        """Test parsing entries with all optional fields"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | duration=1500 | cycle=2 | tag=project\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 1
        assert entries[0].duration_seconds == 1500
        assert entries[0].cycle == 2
        assert entries[0].tag == 'project'
    
    def test_parse_malformed_entries(self, temp_log_file):
        """Test that malformed entries are counted but don't break parsing"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | session_1\n'
            'this is malformed\n'
            'also bad format\n'
            '2025-11-14 11:48:35 | short_break | completed | session_1\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 2
        assert malformed == 2
    
    def test_parse_empty_lines_ignored(self, temp_log_file):
        """Test that empty lines are ignored"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | session_1\n'
            '\n'
            '\n'
            '2025-11-14 11:48:35 | short_break | completed | session_1\n'
        )
        
        entries, malformed = parse_log_file(Path(temp_log_file))
        
        assert len(entries) == 2
        assert malformed == 0


class TestComputeStats:
    """Tests for statistics computation"""
    
    def test_stats_empty_log(self):
        """Test computing stats from empty log"""
        stats = compute_stats([], 0)
        
        assert stats['log_entries'] == 0
        assert stats['malformed_entries'] == 0
        assert stats['sessions']['work']['completed'] == 0
        assert stats['focus']['today_work_sessions_completed'] == 0
        assert stats['focus']['completion_ratio'] == 0.0
        assert stats['streaks']['consecutive_focus_days'] == 0
    
    def test_stats_basic_counts(self):
        """Test basic session counting"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'skipped', 0),
            SessionEntry(now, 'short_break', 'completed', 300),
        ]
        
        stats = compute_stats(entries, 1)
        
        assert stats['log_entries'] == 4
        assert stats['malformed_entries'] == 1
        assert stats['sessions']['work']['completed'] == 2
        assert stats['sessions']['work']['skipped'] == 1
        assert stats['sessions']['short_break']['completed'] == 1
    
    def test_stats_completion_ratio(self):
        """Test completion ratio calculation"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'skipped', 0),
            SessionEntry(now, 'short_break', 'skipped', 0),
        ]
        
        stats = compute_stats(entries, 0)
        
        # 2 completed out of 4 total = 0.5
        assert stats['focus']['completion_ratio'] == 0.5
    
    def test_stats_today_focus(self):
        """Test today's focus time calculation"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),  # 25 minutes
            SessionEntry(now, 'work', 'completed', 1500),  # 25 minutes
            SessionEntry(now, 'short_break', 'completed', 300),  # shouldn't count
        ]
        
        stats = compute_stats(entries, 0)
        
        assert stats['focus']['today_work_sessions_completed'] == 2
        assert stats['focus']['today_focus_minutes'] == 50.0  # 3000 seconds / 60
    
    def test_stats_week_focus(self):
        """Test week focus time calculation"""
        now = datetime.now()
        # Calculate week start (Monday)
        week_start = now.date() - timedelta(days=now.weekday())
        
        # Create entries throughout the week (all within current week boundaries)
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(datetime.combine(week_start, now.time()), 'work', 'completed', 1500),
            SessionEntry(datetime.combine(week_start + timedelta(days=3), now.time()), 'work', 'completed', 1500),
        ]
        
        stats = compute_stats(entries, 0)
        
        # All entries in current week
        assert stats['focus']['week_focus_minutes'] == 75.0  # 4500 seconds / 60
    
    def test_stats_average_duration(self):
        """Test average work session duration"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1800),
            SessionEntry(now, 'work', 'skipped', 0),  # shouldn't count
        ]
        
        stats = compute_stats(entries, 0)
        
        # (1500 + 1800) / 2 = 1650
        assert stats['averages']['avg_work_session_duration_seconds'] == 1650.0
    
    def test_stats_cycles(self):
        """Test cycle counting (4 work sessions = 1 cycle)"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now, 'work', 'completed', 1500),
        ]
        
        stats = compute_stats(entries, 0)
        
        # 6 sessions / 4 = 1 full cycle
        assert stats['cycles']['estimated_full_cycles_completed'] == 1
    
    def test_stats_date_scope(self):
        """Test date scope includes today and week boundaries"""
        stats = compute_stats([], 0)
        
        assert 'date_scope' in stats
        assert 'today' in stats['date_scope']
        assert 'week_start' in stats['date_scope']
        assert 'week_end' in stats['date_scope']


class TestStreakCalculation:
    """Tests for consecutive streak calculation"""
    
    def test_streak_empty_entries(self):
        """Test streak with no entries"""
        streak = _compute_consecutive_streak([])
        assert streak == 0
    
    def test_streak_no_completed_work(self):
        """Test streak with no completed work sessions"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'skipped', 0),
            SessionEntry(now, 'short_break', 'completed', 300),
        ]
        
        streak = _compute_consecutive_streak(entries)
        assert streak == 0
    
    def test_streak_today_only(self):
        """Test streak of 1 day (today)"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
        ]
        
        streak = _compute_consecutive_streak(entries)
        assert streak == 1
    
    def test_streak_consecutive_days(self):
        """Test multi-day consecutive streak"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now - timedelta(days=1), 'work', 'completed', 1500),
            SessionEntry(now - timedelta(days=2), 'work', 'completed', 1500),
        ]
        
        streak = _compute_consecutive_streak(entries)
        assert streak == 3
    
    def test_streak_broken_by_gap(self):
        """Test that streak is broken by a gap day"""
        now = datetime.now()
        entries = [
            SessionEntry(now, 'work', 'completed', 1500),
            SessionEntry(now - timedelta(days=1), 'work', 'completed', 1500),
            # Day 2 missing - breaks streak
            SessionEntry(now - timedelta(days=3), 'work', 'completed', 1500),
        ]
        
        streak = _compute_consecutive_streak(entries)
        assert streak == 2  # Only today and yesterday
    
    def test_streak_no_work_today(self):
        """Test that streak is 0 if no work completed today"""
        now = datetime.now()
        entries = [
            SessionEntry(now - timedelta(days=1), 'work', 'completed', 1500),
            SessionEntry(now - timedelta(days=2), 'work', 'completed', 1500),
        ]
        
        streak = _compute_consecutive_streak(entries)
        assert streak == 0


class TestStatsEndpoint:
    """Integration tests for the /stats endpoint"""
    
    def test_stats_endpoint_success(self, client, monkeypatch, temp_log_file):
        """Test /stats endpoint returns 200 and valid JSON"""
        # Create test log
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | duration=1500\n'
            '2025-11-14 11:48:35 | short_break | completed | duration=300\n'
        )
        
        # Monkeypatch LOG_PATH in app module
        from app import app as flask_app
        monkeypatch.setattr('app.LOG_PATH', Path(temp_log_file))
        
        response = client.get('/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify expected keys
        assert 'generated_at' in data
        assert 'log_entries' in data
        assert 'malformed_entries' in data
        assert 'date_scope' in data
        assert 'sessions' in data
        assert 'focus' in data
        assert 'streaks' in data
        assert 'averages' in data
        assert 'cycles' in data
    
    def test_stats_endpoint_empty_log(self, client, monkeypatch, temp_log_file):
        """Test /stats endpoint with empty log file"""
        Path(temp_log_file).write_text('')
        
        monkeypatch.setattr('app.LOG_PATH', Path(temp_log_file))
        
        response = client.get('/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['log_entries'] == 0
        assert data['sessions']['work']['completed'] == 0
    
    def test_stats_endpoint_with_malformed(self, client, monkeypatch, temp_log_file):
        """Test /stats endpoint handles malformed entries"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | duration=1500\n'
            'malformed entry here\n'
            '2025-11-14 11:48:35 | short_break | completed | duration=300\n'
        )
        
        monkeypatch.setattr('app.LOG_PATH', Path(temp_log_file))
        
        response = client.get('/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['log_entries'] == 2
        assert data['malformed_entries'] == 1
    
    def test_stats_endpoint_error_handling(self, client, monkeypatch):
        """Test /stats endpoint error handling"""
        # Force an error by making generate_stats fail
        def mock_generate_stats(path):
            raise RuntimeError("Test error")
        
        monkeypatch.setattr('app.generate_stats', mock_generate_stats)
        
        response = client.get('/stats')
        
        assert response.status_code == 500
        data = response.get_json()
        
        assert data['status'] == 'error'
        assert data['error_code'] == 'STATS_COMPUTE_FAILED'
        assert 'message' in data


class TestGenerateStats:
    """Tests for the generate_stats convenience function"""
    
    def test_generate_stats_integration(self, temp_log_file):
        """Test generate_stats integrates parsing and computation"""
        Path(temp_log_file).write_text(
            '2025-11-14 11:48:34 | work | completed | duration=1500\n'
            '2025-11-14 11:48:35 | work | completed | duration=1500\n'
        )
        
        stats = generate_stats(Path(temp_log_file))
        
        assert stats['log_entries'] == 2
        assert stats['sessions']['work']['completed'] == 2
        assert stats['sessions']['work']['total_duration_seconds'] == 3000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
