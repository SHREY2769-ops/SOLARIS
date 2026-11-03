"""SOLARIS AI Brain: extensible provider architecture with fallback."""
import base64  # noqa: F401  (kept for clarity: images travel as base64 text)
import requests
import config


class BrainError(Exception):
    pass


# Provider definitions with priorities
PROVIDERS = [
    {"id": "gemini", "name": "Google Gemini", "primary": True, "testable": True},
    {"id": "ollama", "name": "Local Ollama", "primary": False, "testable": False},
]

SYSTEM = (
    f"You are {config.NAME}, a sophisticated personal AI assistant living on the user's own PC. "
    "Tone: calm, sharp, warm and a little witty, like a trusted butler. "
    "Keep answers short (1 to 4 sentences) unless the user asks for depth. "
    "Your replies are often read aloud, so never use markdown, bullet symbols, asterisks or emojis. "
    "For brainstorming, offer a few concrete ideas and end with one good follow-up question. "
    "If a screenshot is attached, it shows what the user is looking at right now; answer about it directly. "
    "The app (not you) handles these commands, and you may tell the user about them: "
    "open <app name>, open the accessibility / wallpaper / music / theme section, "
    "pause / play / next wallpaper, pause / play / next / previous song, volume up / down, "
    "change theme to <color>, how is my PC doing. "
    "For anything about the screen the user can say 'what is on my screen'."
    "Wake phrase: 'Hey Solaris'."
)


def ask(history, image_b64=None, provider_id=None):
    """Ask the AI a question, trying providers in order until one succeeds."""
    # Determine which providers to try
    providers_to_try = []
    if provider_id:
        # Use specified provider first, then fallbacks
        providers_to_try = [p for p in PROVIDERS if p["id"] == provider_id]
        providers_to_try += [p for p in PROVIDERS if p["id"] != provider_id]
    else:
        # Try in priority order
        providers_to_try = PROVIDERS

    last_error = None
    for provider in providers_to_try:
        try:
            return _ask_with_provider(history, image_b64, provider)
        except BrainError as e:
            last_error = e
            continue
        except Exception as e:
            # Non-BrainError exceptions also count as failures
            last_error = BrainError(str(e))
            continue

    # All providers failed
    raise last_error or BrainError("I can't reach any AI provider right now. Check your connection and configuration.")


def _ask_with_provider(history, image_b64, provider):
    """Execute a single provider request."""
    p = next(p for p in PROVIDERS if p["id"] == provider["id"])

    if p["id"] == "gemini":
        return _gemini(history, image_b64)
    elif p["id"] == "ollama":
        return _ollama(history, image_b64)
    else:
        raise BrainError(f"Unknown provider: {provider['id']}")


def _merge(history):
    """Gemini wants user/assistant turns to alternate, so join neighbours of the same kind."""
    merged = []
    for m in history:
        if merged and merged[-1]["role"] == m["role"]:
            merged[-1]["content"] += "\n" + m["content"]
        else:
            merged.append(dict(m))
    return merged


def _gemini(history, image_b64):
    if not config.GEMINI_KEY:
        raise BrainError("I don't have a Gemini key yet. Put it in the .env file, save, and restart me.")
    history = _merge(history)
    contents = []
    for i, m in enumerate(history):
        parts = [{"text": m["content"]}]
        if image_b64 and i == len(history) - 1 and m["role"] == "user":
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_b64}})
        contents.append({"role": "user" if m["role"] == "user" else "model", "parts": parts})
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent"
    try:
        r = requests.post(
            url,
            headers={"x-goog-api-key": config.GEMINI_KEY, "Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": SYSTEM}]},
                "contents": contents,
                "generationConfig": {"maxOutputTokens": 4096},
            },
            timeout=60,
        )
    except requests.RequestException as e:
        raise BrainError("I can't reach the AI right now. Check your internet connection.")
    if r.status_code != 200:
        hints = {
            400: "Google rejected the request. Check that the Gemini key in .env is correct.",
            401: "The Gemini key was rejected. Check it in .env.",
            403: "The Gemini key isn't allowed to do that. Check it in .env.",
            404: "That Gemini model name wasn't found. Check GEMINI_MODEL in .env.",
            429: "The free Gemini limit was reached. Give it a minute and try again.",
        }
        raise BrainError(hints.get(r.status_code, f"The AI service had a problem (code {r.status_code})."))
    data = r.json()
    try:
        text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]).strip()
    except (KeyError, IndexError):
        text = ""
    return text or "I couldn't come up with an answer to that one."


def _ollama(history, image_b64):
    """Query local Ollama model. May raise BrainError if unavailable."""
    import subprocess
    import os
    msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    if image_b64 and msgs:
        msgs[-1]["images"] = [image_b64]
    try:
        # Use creationflags to hide the console window on Windows
        creationflags = 0
        if os.name == "nt":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": config.OLLAMA_MODEL, "messages": [{"role": "system", "content": SYSTEM}] + msgs, "stream": False},
            timeout=300,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception as e:
        raise BrainError("I couldn't reach Ollama. Is it installed and running, with that model downloaded?")