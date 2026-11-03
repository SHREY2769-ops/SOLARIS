"""Wallpaper Engine control. It keeps running in the background; we just send it commands."""
import json
import os
import subprocess
from pathlib import Path
import config

_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
_exe_cache = None
_lib = []

_COMMANDS = {
    "pause": ["pause"],
    "play": ["play"],
    "next": ["nextWallpaper"],
    "mute": ["mute"],
    "unmute": ["unmute"],
}


def exe():
    global _exe_cache
    if _exe_cache:
        return _exe_cache
    if config.WALLPAPER_ENGINE_EXE and Path(config.WALLPAPER_ENGINE_EXE).exists():
        _exe_cache = Path(config.WALLPAPER_ENGINE_EXE)
        return _exe_cache
    if os.name != "nt":
        return None
    places = [r"Program Files (x86)\Steam", r"Program Files\Steam", "SteamLibrary", "Steam",
              r"Games\Steam", r"Games\SteamLibrary"]
    for drive in "CDEFGH":
        for place in places:
            for name in ("wallpaper64.exe", "wallpaper32.exe"):
                p = Path(f"{drive}:\\{place}\\steamapps\\common\\wallpaper_engine\\{name}")
                if p.exists():
                    _exe_cache = p
                    return p
    return None


def _control(*args):
    e = exe()
    if not e:
        return False
    subprocess.Popen([str(e), "-control", *args], cwd=str(e.parent), creationflags=_NO_WINDOW)
    return True


def act(cmd):
    """cmd is one of: pause, play, next, mute, unmute. Returns True if the command was sent."""
    return _control(*_COMMANDS[cmd]) if cmd in _COMMANDS else False


def library():
    """Finds your wallpapers (Workshop downloads and your own) so you can click one."""
    global _lib
    _lib = []
    e = exe()
    if not e:
        return {"found": False, "items": []}
    root = e.parent
    folders = [root.parent.parent / "workshop" / "content" / "431960",
               root / "projects" / "myprojects", root / "projects" / "defaultprojects"]
    for folder in folders:
        if not folder.exists():
            continue
        for item in sorted(folder.iterdir()):
            pj = item / "project.json"
            if not pj.exists() or len(_lib) >= 400:
                continue
            try:
                data = json.loads(pj.read_text(encoding="utf-8-sig", errors="ignore"))
            except Exception:
                continue
            prev = item / data.get("preview", "") if data.get("preview") else None
            _lib.append({"json": str(pj), "title": data.get("title") or item.name,
                         "preview": str(prev) if prev and prev.exists() else None})
    return {"found": True, "items": [{"id": i, "title": w["title"], "preview": bool(w["preview"])}
                                     for i, w in enumerate(_lib)]}


def set_by_id(i):
    if 0 <= i < len(_lib) and _control("openWallpaper", "-file", _lib[i]["json"]):
        return _lib[i]["title"]
    return None


def preview_path(i):
    return _lib[i]["preview"] if 0 <= i < len(_lib) else None