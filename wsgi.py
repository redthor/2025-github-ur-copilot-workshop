"""
WSGI configuration for Pomodoro Timer application on Azure App Service
"""
import os
import sys

# Add the project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application
from pomodoro_app.app import app

# This is the WSGI application object that Azure App Service will use
application = app

if __name__ == "__main__":
    application.run()