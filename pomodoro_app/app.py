from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Ensure log file exists
LOG_FILE = 'pomodoro_log.txt'

@app.route('/')
def index():
    """Serve the main timer page"""
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log_session():
    """Log pomodoro session events"""
    try:
        data = request.get_json()
        
        # Extract session data
        session_type = data.get('session_type', 'work')  # work, short_break, long_break
        action = data.get('action', 'completed')  # completed, skipped
        session_number = data.get('session_number', 1)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log entry format: timestamp | session_type | action | session_number
        log_entry = f"{timestamp} | {session_type} | {action} | session_{session_number}\n"
        
        # Append to log file
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        return jsonify({'status': 'success', 'message': 'Session logged successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/history')
def get_history():
    """Optional endpoint to retrieve session history"""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({'sessions': []})
        
        sessions = []
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(' | ')
                    if len(parts) == 4:
                        sessions.append({
                            'timestamp': parts[0],
                            'session_type': parts[1],
                            'action': parts[2],
                            'session_number': parts[3]
                        })
        
        return jsonify({'sessions': sessions})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Use environment variables for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)