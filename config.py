"""SOLARIS Configuration: settings, branding, and environment."""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)


def _load_env():
    f = BASE / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()


def get(name, default=""):
    return os.environ.get(name) or default

# === Branding ===
NAME = get("ASSISTANT_NAME", "SOLARIS")
VERSION = get("APP_VERSION", "1.0.0")
WAKE_PHRASE = get("WAKE_PHRASE", "Hey Solaris").lower()

# === AI Provider Settings ===
PROVIDER = get("AI_PROVIDER", "gemini").lower()          # gemini or ollama
GEMINI_KEY = get("GEMINI_API_KEY")
GEMINI_MODEL = get("GEMINI_MODEL", "gemini-2.5-flash")
OLLAMA_MODEL = get("OLLAMA_MODEL", "llama3.2-vision")

# === Voice Settings ===
VOICE_STYLE = get("VOICE_STYLE", "A")  # A: Natural, B: Deep Cinematic
VOICE = get("VOICE", "en-US-JennyNeural")
SPEED = float(get("SPEED", "1.0"))
MICROPHONE = get("MICROPHONE")

# === Wake Word ===
ENABLE_WAKE_WORD = get("ENABLE_WAKE_WORD", "true").lower() == "true"

# === Interface Settings ===
ORB_RADIUS = int(get("ORB_RADIUS", "60"))
ORB_OPACITY = float(get("ORB_OPACITY", "1.0"))
SHOW_TOOLTIPS = get("SHOW_TOOLTIPS", "true").lower() == "true"

# === Windows Integration ===
ENABLE_STARTUP = get("ENABLE_WINDOWS_STARTUP", "false").lower() == "true"
SYSTEM_TRAY = get("SYSTEM_TRAY", "true").lower() == "true"

# === Serious Mode ===
ENABLE_SERIOUS_MODE = get("ENABLE_SERIOUS_MODE", "true").lower() == "true"

# === Reminders ===
ENABLE_REMINDERS = get("ENABLE_REMINDERS", "true").lower() == "true"

# === Focus Mode ===
ENABLE_FOCUS_MODE = get("ENABLE_FOCUS_MODE", "true").lower() == "true"

# === Health / Telemetry ===
LHM_URL = get("LIBRE_HARDWARE_MONITOR_URL", "http://localhost:8085/data.json")
HIDE_ON_CAPTURE = get("HIDE_ON_CAPTURE", "true").lower() == "true"
PORT = int(get("PORT", "5005"))