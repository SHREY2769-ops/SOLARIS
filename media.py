"""Music: reads what's playing (Spotify, YouTube in a browser...) and presses play/pause/next."""
import asyncio
import ctypes
import os

try:
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as _Manager
    AVAILABLE = True
except Exception:
    AVAILABLE = False


async def _session():
    manager = await _Manager.request_async()
    return manager.get_current_session()


async def _now():
    s = await _session()
    if not s:
        return {"active": False}
    info = await s.try_get_media_properties_async()
    playing = int(s.get_playback_info().playback_status) == 4     # 4 = Playing
    app = (s.source_app_user_model_id or "").lower()
    if "spotify" in app:
        source = "Spotify"
    elif any(b in app for b in ("chrome", "edge", "opera", "firefox", "brave")):
        source = "Browser"
    else:
        source = s.source_app_user_model_id or ""
    return {"active": True, "title": info.title, "artist": info.artist, "playing": playing, "source": source}


_METHODS = {
    "toggle": "try_toggle_play_pause_async",
    "play": "try_play_async",
    "pause": "try_pause_async",
    "next": "try_skip_next_async",
    "previous": "try_skip_previous_async",
}


async def _do(cmd):
    s = await _session()
    if not s:
        return False
    return bool(await getattr(s, _METHODS[cmd])())


def now_playing():
    if not AVAILABLE:
        return {"available": False, "active": False}
    try:
        data = asyncio.run(_now())
    except Exception:
        data = {"active": False}
    data["available"] = True
    return data


def control(cmd):
    if not AVAILABLE or cmd not in _METHODS:
        return False
    try:
        return asyncio.run(_do(cmd))
    except Exception:
        return False


_KEYS = {"up": 0xAF, "down": 0xAE, "mute": 0xAD}


def volume(direction, steps=5):
    """Presses the keyboard's volume keys (works for the whole PC)."""
    if os.name != "nt" or direction not in _KEYS:
        return False
    press = ctypes.windll.user32.keybd_event
    for _ in range(1 if direction == "mute" else steps):
        press(_KEYS[direction], 0, 0, 0)
        press(_KEYS[direction], 0, 2, 0)
    return True