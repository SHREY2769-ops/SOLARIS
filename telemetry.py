"""Hardware telemetry: CPU, memory, GPU, disk, network, battery (+ temperatures and fans if
LibreHardwareMonitor is running)."""
import os
import re
import shutil
import subprocess
import time
import psutil
import requests
import config

psutil.cpu_percent(None)        # first reading is always 0, so take one now
_last_net = None
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
_CPU_NAMES = {"CPU Package", "Core (Tctl/Tdie)", "CPU (Tctl/Tdie)", "Core Average", "CPU Total"}


def _gpu():
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total,power.draw",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3, creationflags=_NO_WINDOW,
        ).stdout.strip().splitlines()[0]
        name, util, temp, used, total, power = [x.strip() for x in out.split(",")]

        def num(v):
            try:
                return float(v)
            except ValueError:
                return None
        return {"name": name, "util": num(util), "temp": num(temp), "mem_used": num(used),
                "mem_total": num(total), "power": num(power)}
    except Exception:
        return None


def _number(text):
    m = re.search(r"-?\d+(?:[.,]\d+)?", text)
    return float(m.group().replace(",", ".")) if m else None


def _sensors():
    try:
        tree = requests.get(config.LHM_URL, timeout=0.6).json()
    except Exception:
        return None
    temps, fans = {}, []

    def walk(node):
        name, value = node.get("Text", ""), str(node.get("Value", ""))
        if "°C" in value:
            v = _number(value)
            if v is not None:
                if name in _CPU_NAMES and "cpu" not in temps:
                    temps["cpu"] = v
                elif name == "GPU Core" and "gpu" not in temps:
                    temps["gpu"] = v
        elif "RPM" in value:
            v = _number(value.replace(",", "").replace(".", ""))
            if v is not None and v > 0:
                fans.append({"name": name, "rpm": int(v)})
        for child in node.get("Children", []):
            walk(child)

    walk(tree)
    return {"temps": temps, "fans": fans}


def snapshot():
    global _last_net
    now, net = time.time(), psutil.net_io_counters()
    down = up = 0.0
    if _last_net:
        dt = max(now - _last_net[0], 0.001)
        down, up = (net.bytes_recv - _last_net[1]) / dt, (net.bytes_sent - _last_net[2]) / dt
    _last_net = (now, net.bytes_recv, net.bytes_sent)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage((os.environ.get("SystemDrive", "C:") + "\\") if os.name == "nt" else "/")
    bat = psutil.sensors_battery()
    return {
        "cpu": psutil.cpu_percent(None),
        "ram": mem.percent,
        "ram_used_gb": round(mem.used / 2**30, 1),
        "ram_total_gb": round(mem.total / 2**30, 1),
        "disk": disk.percent,
        "disk_free_gb": round(disk.free / 2**30),
        "net_down": down,
        "net_up": up,
        "battery": round(bat.percent) if bat else None,
        "plugged": bool(bat.power_plugged) if bat else None,
        "gpu": _gpu(),
        "sensors": _sensors(),
    }


def spoken():
    d = snapshot()
    parts = [f"CPU at {round(d['cpu'])} percent", f"memory at {round(d['ram'])} percent"]
    if d["gpu"] and d["gpu"]["util"] is not None:
        parts.append(f"graphics at {round(d['gpu']['util'])} percent")
    if d["battery"] is not None:
        parts.append(f"battery at {d['battery']} percent" + (" and charging" if d["plugged"] else ""))
    return "Right now: " + ", ".join(parts) + "."
