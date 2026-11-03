"""Apps: finds the programs in your Start menu (with their logos) so you can launch them."""
import difflib
import json
import os
import subprocess
import config

ICONS = config.DATA / "icons"
CACHE = config.DATA / "apps.json"
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# Built-in Windows tools that don't live in the Start menu as normal shortcuts.
SYSTEM_TILES = [
    {"id": "sys-settings", "name": "Settings", "uri": "ms-settings:"},
    {"id": "sys-explorer", "name": "File Explorer", "cmd": ["explorer.exe"]},
    {"id": "sys-taskmgr", "name": "Task Manager", "cmd": ["taskmgr.exe"]},
    {"id": "sys-calc", "name": "Calculator", "uri": "calculator:"},
    {"id": "sys-control", "name": "Control Panel", "cmd": ["control.exe"]},
    {"id": "sys-store", "name": "Microsoft Store", "uri": "ms-windows-store:"},
]

_PS = r'''
Add-Type -AssemblyName System.Drawing
$out = $args[0]; $iconDir = $args[1]
$roots = @("$env:ProgramData\Microsoft\Windows\Start Menu\Programs", "$env:APPDATA\Microsoft\Windows\Start Menu\Programs")
$skip = 'uninstall|readme|release notes|license|documentation|help|website|manual|changelog'
$seen = @{}; $items = @(); $i = 0
foreach ($root in $roots) {
  if (-not (Test-Path $root)) { continue }
  Get-ChildItem -Path $root -Filter *.lnk -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $name = $_.BaseName
    if ($name -match $skip) { return }
    if ($seen.ContainsKey($name.ToLower())) { return }
    $seen[$name.ToLower()] = $true
    $i++
    $png = Join-Path $iconDir "$i.png"
    $has = $false
    try {
      $ico = [System.Drawing.Icon]::ExtractAssociatedIcon($_.FullName)
      $bmp = $ico.ToBitmap(); $bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
      $bmp.Dispose(); $ico.Dispose(); $has = $true
    } catch { }
    $items += [pscustomobject]@{ id = "app-$i"; name = $name; path = $_.FullName; icon = $has }
  }
}
ConvertTo-Json -InputObject @($items) -Compress | Set-Content -Path $out -Encoding UTF8
'''


def scan():
    if os.name != "nt":
        return
    ICONS.mkdir(exist_ok=True)
    for old in ICONS.glob("*.png"):
        old.unlink()
    script = config.DATA / "scan_apps.ps1"
    script.write_text(_PS, encoding="utf-8")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(script), str(CACHE), str(ICONS)], timeout=240, creationflags=_NO_WINDOW)


def _all(force=False):
    if force or not CACHE.exists():
        scan()
    try:
        found = json.loads(CACHE.read_text(encoding="utf-8-sig"))
    except Exception:
        found = []
    if isinstance(found, dict):
        found = [found]
    found.sort(key=lambda a: a["name"].lower())
    return SYSTEM_TILES + found


def list_public(force=False):
    return [{"id": a["id"], "name": a["name"], "icon": bool(a.get("icon"))} for a in _all(force)]


def icon_path(app_id):
    if app_id.startswith("app-") and app_id[4:].isdigit():
        p = ICONS / f"{app_id[4:]}.png"
        return p if p.exists() else None
    return None


def _start(a):
    if "uri" in a:
        os.startfile(a["uri"])
    elif "cmd" in a:
        subprocess.Popen(a["cmd"])
    else:
        os.startfile(a["path"])
    return a["name"]


def launch(app_id):
    for a in _all():
        if a["id"] == app_id:
            return _start(a)
    return None


def find(query):
    """Finds an app by a spoken name, e.g. 'steam' or 'opera'."""
    q = query.lower().strip()
    items = _all()
    names = {a["name"].lower(): a for a in items}
    if q in names:
        return names[q]
    for n, a in names.items():
        if n.startswith(q):
            return a
    for n, a in names.items():
        if q in n:
            return a
    close = difflib.get_close_matches(q, list(names), n=1, cutoff=0.6)
    return names[close[0]] if close else None


def launch_by_name(query):
    a = find(query)
    return _start(a) if a else None