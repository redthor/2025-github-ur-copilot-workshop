# GitHub Copilot Workshop

This is a sample repository for GitHub Copilot Workshop at GitHub Universe Recap 2025, Jakarta, Indonesia.

Using the files in this repository, we created a fully functional **Pomodoro Timer Web Application** using Python (Flask), JavaScript, HTML, and CSS.

## 🎯 What is This Project?

A production-ready Pomodoro Timer web application that helps you stay focused and productive using the Pomodoro Technique. The app features:

- ⏱️ **25-minute work sessions** with short and long breaks
- 📊 **Session tracking** with visual progress indicators
- ⚙️ **Customizable timers** for work and break durations
- 📝 **Automatic logging** of all sessions
- 🔔 **Browser notifications** when sessions complete
- 📱 **Responsive design** that works on all devices

## 🌐 Live Demo

The application is deployed and available at:
**http://pomodoro-timer-ecomindo-1763110994.azurewebsites.net/**

## 📚 Documentation

- **[Architecture](architecture.md)** - System design and technical architecture
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Detailed development progress and features
- **[Pomodoro App README](pomodoro_app/README.md)** - Application-specific documentation
- **[Development Plan](plan.md)** - Original project plan and requirements
- **[Pomodoro Technique Guide](Pomodoro_Technique.md)** - Learn about the productivity method

## 🚀 Quick Start

### Prerequisites

You need to have `uv` installed for this project.

#### Installing uv

`uv` is an extremely fast Python package and project manager, written in Rust. Install it using one of these methods:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or visit the [official installation guide](https://docs.astral.sh/uv/#installation) for more options.

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eComindo/2025-github-ur-copilot-workshop.git
   cd 2025-github-ur-copilot-workshop
   ```

2. **Create and activate virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   cd pomodoro_app
   python app.py
   ```

5. **Open your browser:**
   Navigate to `http://127.0.0.1:5000`

### Deactivating Virtual Environment

When you're done working:
```bash
deactivate
```

## 📁 Project Structure

```
2025-github-ur-copilot-workshop/
├── pomodoro_app/           # Main application directory
│   ├── app.py             # Flask backend server
│   ├── static/            # CSS and JavaScript files
│   │   ├── style.css      # Application styling
│   │   └── timer.js       # Timer logic and UI interactions
│   ├── templates/         # HTML templates
│   │   └── index.html     # Main application page
│   ├── test_app.py        # Test suite
│   ├── pomodoro_log.txt   # Session logs (generated)
│   └── README.md          # App-specific documentation
├── wsgi.py                # WSGI entry point for production
├── startup.txt            # Azure deployment startup command
├── requirements.txt       # Python dependencies
├── architecture.md        # Technical architecture
├── IMPLEMENTATION_SUMMARY.md  # Development summary
└── README.md             # This file
```

## 🔧 Dependencies

The project uses the following Python packages:

- **Flask 3.1.2** - Web framework
- **gunicorn 21.2.0** - Production WSGI server
- **requests 2.32.5** - HTTP library for testing

## 🌟 Key Features

### Timer Functionality
- Accurate countdown timer with pause/resume
- Automatic transitions between work and break sessions
- Visual progress tracking through 4-session cycles
- Skip to next session option

### User Experience
- Modern, clean interface
- Responsive design for mobile and desktop
- Customizable session durations
- Persistent settings using localStorage
- Browser notifications

### Data Management
- Automatic session logging to file
- Timestamped entries for all events
- Session history API endpoint
- Completion vs. skip tracking

## 🚢 Deployment

The application is deployed on **Azure App Service** using:
- **WSGI server**: Gunicorn
- **Configuration**: See `wsgi.py` and `startup.txt`
- **Environment**: Production-ready Flask configuration

### Testing the Deployed API

```bash
# Check session history
curl http://pomodoro-timer-ecomindo-1763110994.azurewebsites.net/history
```

## 🛠️ Development

### Running Tests

```bash
source .venv/bin/activate
cd pomodoro_app
python -m pytest test_app.py
```

### Running in Debug Mode

The app runs in debug mode by default during local development:
```bash
python app.py
```

## 🤝 Contributing

This project was built as part of a GitHub Copilot workshop. Feel free to:
- Fork the repository
- Create feature branches
- Submit pull requests
- Open issues for bugs or enhancements

## 📖 Learning Resources

This project demonstrates:
- **Flask web development** with modern Python
- **Frontend-backend integration** using AJAX
- **Session management** and logging
- **Responsive web design** with CSS
- **Production deployment** to Azure
- **Test-driven development** practices

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

Created for GitHub Universe Recap 2025 workshop in Jakarta, Indonesia, demonstrating the power of GitHub Copilot for rapid application development.