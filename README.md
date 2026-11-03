# SOLARIS: your personal AI assistant

![SOLARIS Logo](Abstract%20Logo.jpg)

Double-click `start_solaris.bat` to run it. The first time, it sets itself up and opens a settings file.

## Quick Start

1. Double-click `start_solaris.bat` to launch SOLARIS
2. A command window will open and the web interface will start
3. Open your browser and go to `http://localhost:5005`
4. Follow the on-screen instructions to configure your AI key

## First-Time Configuration

1. Copy `.env.example` to `.env`
2. Paste your Google Gemini API key after `GEMINI_API_KEY=`
3. Save and close the file
4. Restart SOLARIS

## Voice Commands

### Wake Word
- "Hey Solaris" - Activate SOLARIS (if wake word is enabled)
- "Hey Solaris, open [app]" - Open applications
- "Hey Solaris, change theme to [color]" - Change visual theme
- "Hey Solaris, what's the time" - Check time
- "Hey Solaris, how is my PC doing" - System status

### Dashboard Controls
- Open Chrome, YouTube, Instagram, Notepad, or any application
- Play/pause/skip music controls
- Change wallpaper
- Adjust volume
- Toggle mute

### Conversation
- Just type or speak naturally to SOLARIS
- Ask questions, get help with tasks
- SOLARIS remembers conversation context

## Features

### Floating Orb
- Draggable widget that lives on your desktop
- Changes color based on assistant state
- States: idle, listening, thinking, speaking, error
- Click to open the main homepage

### AI Brain
- **Primary**: Google Gemini (online, fastest)
- **Fallback**: Local Ollama (if available, private)
- Automatic provider switching when primary is unavailable
- Conversation context preserved across providers

### Voice System
- **Voice A**: Natural, human-like conversational voice
- **Voice B**: Deep, cinematic SOLARIS/JARVIS-inspired voice
- Push-to-talk support
- Toggle hotkey listening
- Optional "Hey Solaris" wake word
- Speech-to-text and text-to-speech
- Microphone selection

### Windows Integration
- System tray integration
- Optional Windows startup on login
- Single instance prevention
- Debugging launcher available
- Keeps terminal hidden during normal operation

### Serious Mode
- Dark crimson/red theme for focused research
- Multi-source research with fact verification
- Source links and publication dates included
- Structured reports with conclusions
- Can be interrupted and resumed

### Reminders System
- Create reminders with natural language
- "Remind me in ten minutes"
- "Remind me to finish science homework at 6 PM"
- Persistent storage, desktop notifications
- Mark completed, edit, cancel

### Focus Mode
- Distraction-free interface
- Configurable focus timer
- Break reminders
- Reduced animations and interruptions
- Easy exit

### Knowledge Library
- Persistent knowledge storage across sessions
- Organized categories (AI, programming, science, history, etc.)
- Searchable knowledge library
- Weekly "What I Learned" reports
- Duplicate detection and prevention

### Desktop Control
- Open applications and websites
- Validate commands before execution
- Handle unavailable applications gracefully
- Ask for confirmation before sensitive operations

### Theme System
- 12+ futuristic themes (cyan, azure, violet, magenta, crimson, orange, amber, lime, green, teal, rose, silver)
- Serious Mode with crimson theme
- Customizable orb colors
- Theme aliases and shortcuts

## Configuration

Edit the `.env` file to customize:

- **AI Provider**: gemini (default) or ollama
- **Voice Style**: A (natural) or B (cinematic)
- **Windows Startup**: Enable/disable auto-launch
- **System Tray**: Show/hide tray icon
- **Themes**: Choose your preferred color scheme
- **Wake Word**: Enable/disable "Hey Solaris"

## Project Structure

```
SOLARIS/
├── app.py                  # Main Flask application
├── brain.py                # AI provider architecture
├── commands.py             # Desktop command routing
├── config.py               # Settings and branding
├── voice.py                # Advanced voice system
├── themes.py               # Theme colors
├── apps.py                 # Application launcher
├── media.py                # Media controls
├── screen.py               # Screenshot capture
├── telemetry.py            # System health monitoring
├── wallpaper.py            # Wallpaper Engine integration
├── telemetry.py            # Hardware monitoring
├── start_solaris.bat       # Windows launcher
├── start_jarvis.bat        # Original JARVIS launcher (preserved)
├── .env.example            # Configuration template
├── public/                 # Frontend interface
│   ├── index.html          # Main HTML page
│   ├── styles.css          # Futuristic orb & dashboard styling
│   └── app.js              # Frontend logic
├── data/                   # Persistent data storage
└── Abstract Logo.jpg       # SOLARIS logo
```

## Requirements

See `requirements.txt` for Python dependencies.

## License

This project is for personal use. Keep your API keys secure and never commit .env files with real credentials.