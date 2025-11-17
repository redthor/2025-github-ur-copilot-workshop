"""
Unit tests for Pomodoro Timer Flask Application
Tests all routes and functionality
"""
import pytest
import json
import os
import tempfile
from app import app, LOG_FILE


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    
    # Create a temporary log file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        test_log_file = tmp_file.name
    
    # Temporarily replace LOG_FILE
    original_log_file = app.config.get('LOG_FILE', LOG_FILE)
    app.config['LOG_FILE'] = test_log_file
    
    with app.test_client() as client:
        yield client
    
    # Cleanup: remove temporary log file
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
    
    # Restore original log file
    app.config['LOG_FILE'] = original_log_file


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        temp_file_path = tmp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


class TestIndexRoute:
    """Tests for the index route"""
    
    def test_index_returns_200(self, client):
        """Test that index route returns 200 status code"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_returns_html(self, client):
        """Test that index route returns HTML content"""
        response = client.get('/')
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestLogSessionRoute:
    """Tests for the /log route"""
    
    def test_log_work_session_success(self, client, monkeypatch, temp_log_file):
        """Test logging a completed work session"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert 'Session logged successfully' in json_data['message']
        
        # Verify log file content
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert 'work' in log_content
            assert 'completed' in log_content
            assert 'session_1' in log_content
    
    def test_log_short_break_session(self, client, monkeypatch, temp_log_file):
        """Test logging a short break session"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {
            'session_type': 'short_break',
            'action': 'completed',
            'session_number': 2
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        
        # Verify log file content
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert 'short_break' in log_content
            assert 'session_2' in log_content
    
    def test_log_long_break_session(self, client, monkeypatch, temp_log_file):
        """Test logging a long break session"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {
            'session_type': 'long_break',
            'action': 'completed',
            'session_number': 4
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        
        # Verify log file content
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert 'long_break' in log_content
            assert 'session_4' in log_content
    
    def test_log_skipped_session(self, client, monkeypatch, temp_log_file):
        """Test logging a skipped session"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {
            'session_type': 'work',
            'action': 'skipped',
            'session_number': 3
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        
        # Verify log file content
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert 'skipped' in log_content
    
    def test_log_with_default_values(self, client, monkeypatch, temp_log_file):
        """Test logging with default values when optional fields are missing"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {}  # Empty data should use defaults
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        
        # Verify log file contains default values
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
            assert 'work' in log_content  # default session_type
            assert 'completed' in log_content  # default action
            assert 'session_1' in log_content  # default session_number
    
    def test_log_multiple_sessions(self, client, monkeypatch, temp_log_file):
        """Test logging multiple sessions"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        sessions = [
            {'session_type': 'work', 'action': 'completed', 'session_number': 1},
            {'session_type': 'short_break', 'action': 'completed', 'session_number': 1},
            {'session_type': 'work', 'action': 'completed', 'session_number': 2},
        ]
        
        for session in sessions:
            response = client.post('/log',
                                  data=json.dumps(session),
                                  content_type='application/json')
            assert response.status_code == 200
        
        # Verify log file has all entries
        with open(temp_log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
    
    def test_log_with_invalid_json(self, client):
        """Test logging with invalid JSON data"""
        response = client.post('/log',
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data['status'] == 'error'
    
    def test_log_without_content_type(self, client, monkeypatch, temp_log_file):
        """Test logging without proper content type header"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log', data=json.dumps(data))
        
        # Should still work but may have issues parsing
        assert response.status_code in [200, 400, 500]


class TestHistoryRoute:
    """Tests for the /history route"""
    
    def test_history_empty_log(self, client, monkeypatch, temp_log_file):
        """Test retrieving history when log file is empty"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        response = client.get('/history')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        assert json_data['sessions'] == []
    
    def test_history_with_sessions(self, client, monkeypatch, temp_log_file):
        """Test retrieving history with logged sessions"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        # Log some sessions first
        sessions_data = [
            {'session_type': 'work', 'action': 'completed', 'session_number': 1},
            {'session_type': 'short_break', 'action': 'completed', 'session_number': 1},
        ]
        
        for session in sessions_data:
            client.post('/log',
                       data=json.dumps(session),
                       content_type='application/json')
        
        # Retrieve history
        response = client.get('/history')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        assert len(json_data['sessions']) == 2
        
        # Verify session data structure
        first_session = json_data['sessions'][0]
        assert 'timestamp' in first_session
        assert 'session_type' in first_session
        assert 'action' in first_session
        assert 'session_number' in first_session
        assert first_session['session_type'] == 'work'
        assert first_session['action'] == 'completed'
    
    def test_history_nonexistent_log_file(self, client, monkeypatch):
        """Test retrieving history when log file doesn't exist"""
        # Point to a non-existent file
        monkeypatch.setattr('app.LOG_FILE', '/tmp/nonexistent_pomodoro_log.txt')
        
        response = client.get('/history')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        assert json_data['sessions'] == []
    
    def test_history_with_malformed_log_entries(self, client, monkeypatch, temp_log_file):
        """Test retrieving history with malformed log entries"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        # Write some malformed log entries
        with open(temp_log_file, 'w') as f:
            f.write("2024-01-01 10:00:00 | work | completed | session_1\n")
            f.write("malformed entry\n")  # This should be skipped
            f.write("2024-01-01 10:25:00 | short_break | completed | session_1\n")
            f.write("\n")  # Empty line should be skipped
        
        response = client.get('/history')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        # Should only return 2 valid entries
        assert len(json_data['sessions']) == 2
    
    def test_history_returns_correct_structure(self, client, monkeypatch, temp_log_file):
        """Test that history returns correct data structure"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        # Log a session
        session_data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 5
        }
        
        client.post('/log',
                   data=json.dumps(session_data),
                   content_type='application/json')
        
        # Retrieve history
        response = client.get('/history')
        json_data = response.get_json()
        
        assert len(json_data['sessions']) == 1
        session = json_data['sessions'][0]
        
        # Verify all fields are present
        assert session['session_type'] == 'work'
        assert session['action'] == 'completed'
        assert session['session_number'] == 'session_5'
        assert 'timestamp' in session


class TestLogFileIntegrity:
    """Tests for log file integrity and format"""
    
    def test_log_file_format(self, client, monkeypatch, temp_log_file):
        """Test that log entries follow the correct format"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        client.post('/log',
                   data=json.dumps(data),
                   content_type='application/json')
        
        # Read and verify format
        with open(temp_log_file, 'r') as f:
            line = f.readline().strip()
            parts = line.split(' | ')
            
            assert len(parts) == 4
            # Verify timestamp format (basic check)
            assert len(parts[0]) > 0
            assert parts[1] == 'work'
            assert parts[2] == 'completed'
            assert parts[3] == 'session_1'
    
    def test_log_file_append_mode(self, client, monkeypatch, temp_log_file):
        """Test that log entries are appended, not overwritten"""
        monkeypatch.setattr('app.LOG_FILE', temp_log_file)
        
        # Log first session
        client.post('/log',
                   data=json.dumps({'session_type': 'work', 'action': 'completed', 'session_number': 1}),
                   content_type='application/json')
        
        # Log second session
        client.post('/log',
                   data=json.dumps({'session_type': 'work', 'action': 'completed', 'session_number': 2}),
                   content_type='application/json')
        
        # Verify both entries exist
        with open(temp_log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert 'session_1' in lines[0]
            assert 'session_2' in lines[1]


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_log_route_handles_exceptions(self, client, monkeypatch):
        """Test that log route handles exceptions gracefully"""
        # Mock LOG_FILE to cause an error
        def mock_open(*args, **kwargs):
            raise PermissionError("Cannot write to file")
        
        monkeypatch.setattr('builtins.open', mock_open)
        
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data['status'] == 'error'
        assert 'message' in json_data
    
    def test_history_route_handles_exceptions(self, client, monkeypatch):
        """Test that history route handles read exceptions"""
        def mock_exists(path):
            return True
        
        def mock_open(*args, **kwargs):
            raise PermissionError("Cannot read file")
        
        monkeypatch.setattr('os.path.exists', mock_exists)
        monkeypatch.setattr('builtins.open', mock_open)
        
        response = client.get('/history')
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data['status'] == 'error'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
