"""Settings. Reads the .env file so your secret key stays out of the code."""
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


NAME = get("ASSISTANT_NAME", "SOLARIS")
PORT = int(get("PORT", "5005"))
PROVIDER = get("AI_PROVIDER", "gemini").lower()          # gemini or ollama
GEMINI_KEY = get("GEMINI_API_KEY")
GEMINI_MODEL = get("GEMINI_MODEL", "gemini-2.5-flash")
OLLAMA_MODEL = get("OLLAMA_MODEL", "llama3.2-vision")
VOICE = get("VOICE", "en-GB-RyanNeural")
WALLPAPER_ENGINE_EXE = get("WALLPAPER_ENGINE_PATH")
LHM_URL = get("LIBRE_HARDWARE_MONITOR_URL", "http://localhost:8085/data.json")
HIDE_ON_CAPTURE = get("HIDE_ON_CAPTURE", "true").lower() == "true"
