"""SOLARIS: the main program. Run this file to start everything."""

import subprocess
import sys
import threading
import time
import webbrowser
from flask import Flask, Response, abort, jsonify, request, send_file, send_from_directory

import apps
import brain
import commands
import config
import media
import screen
import telemetry
import themes
import voice
import wallpaper

app = Flask(__name__, static_folder="public", static_url_path="")

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

_HOSTS = {f"localhost:{config.PORT}", f"127.0.0.1:{config.PORT}"}


@app.before_request
def guard():
    """Only this app's own page may talk to the server (protects against other websites)."""
    if request.host not in _HOSTS:
        abort(403)
    if request.method == "POST":
        origin = request.headers.get("Origin")
        if origin and origin not in {f"http://{h}" for h in _HOSTS}:
            abort(403)


def _json():
    return request.get_json(silent=True) or {}


@app.get("/")
def index():
    return send_from_directory("public", "index.html")


@app.get("/api/status")
def status():
    ready = bool(config.GEMINI_KEY) if config.PROVIDER == "gemini" else True
    return jsonify(
        name=config.NAME,
        version=config.VERSION,
        configured=ready,
        themes=themes.public(),
        provider=config.PROVIDER,
        voice_style=config.VOICE_STYLE,
    )


@app.post("/api/chat")
def chat():
    body = _json()
    msgs = [
        {"role": m["role"], "content": str(m["content"])[:6000]}
        for m in body.get("messages", [])
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ][-24:]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    if not msgs or msgs[-1]["role"] != "user":
        return jsonify(error="Nothing to send."), 400
    text = msgs[-1]["content"]

    # Route through AI brain with provider fallback
    try:
        reply = brain.ask(msgs)
    except brain.BrainError as e:
        return jsonify(error=str(e)), 502

    # Also check for commands
    cmd = commands.route(text)
    if cmd:
        return jsonify(reply=cmd["reply"], action=cmd["action"], screen=False)

    image = None
    if body.get("screen") or commands.wants_screen(text):
        try:
            image = screen.capture_b64(window_title=config.NAME)
        except Exception as e:
            return jsonify(error=f"I couldn't capture the screen: {e}"), 500
    return jsonify(reply=reply, screen=bool(image))


@app.get("/api/telemetry")
def get_telemetry():
    return jsonify(telemetry.snapshot())


@app.get("/api/apps")
def get_apps():
    return jsonify(apps=apps.list_public())


@app.post("/api/apps/rescan")
def rescan_apps():
    return jsonify(apps=apps.list_public(force=True))


@app.post("/api/apps/launch")
def launch_app():
    name = apps.launch(str(_json().get("id", "")))
    if not name:
        return jsonify(error="I couldn't open that app."), 404
    return jsonify(message=f"Opening {name}.")


@app.get("/api/apps/icon/<app_id>")
def app_icon(app_id):
    p = apps.icon_path(app_id)
    return send_file(p, mimetype="image/png") if p else abort(404)


@app.get("/api/wallpaper/library")
def wp_library():
    return jsonify(wallpaper.library())


@app.get("/api/wallpaper/preview/<int:i>")
def wp_preview(i):
    p = wallpaper.preview_path(i)
    return send_file(p) if p else abort(404)


@app.post("/api/wallpaper/control")
def wp_control():
    ok = wallpaper.act(str(_json().get("cmd", "")))
    if not ok:
        return jsonify(error="I couldn't reach Wallpaper Engine. Check the setup guide."), 502
    return jsonify(message="Done.")


@app.post("/api/wallpaper/set")
def wp_set():
    try:
        title = wallpaper.set_by_id(int(_json().get("id", -1)))
    except (TypeError, ValueError):
        title = None
    if not title:
        return jsonify(error="I couldn't change the wallpaper."), 502
    return jsonify(message=f"Wallpaper set to {title}.")


@app.get("/api/media")
def get_media():
    return jsonify(media.now_playing())


@app.post("/api/media/control")
def media_control():
    ok = media.control(str(_json().get("cmd", "")))
    return (jsonify(message="Done."), 200) if ok else (jsonify(error="Nothing is playing right now."), 404)


@app.post("/api/volume")
def volume():
    media.volume(str(_json().get("dir", "")))
    return jsonify(message="Done.")


@app.post("/api/tts")
def tts():
    text = voice.clean(str(_json().get("text", "")))[:1200]
    if not text:
        abort(400)
    try:
        audio = voice.synth(text)
    except Exception:
        return jsonify(error="The voice service isn't available."), 502
    return Response(audio, mimetype="audio/mpeg")


@app.post("/api/voice/style")
def voice_style():
    """Set the voice style."""
    style = str(_json().get("style", ""))
    if voice.set_voice_style(style):
        return jsonify(message=f"Voice style set to {style}")
    return jsonify(error="Invalid voice style."), 400


@app.post("/api/voice/speak")
def voice_speak():
    """Text-to-speech."""
    text = str(_json().get("text", ""))
    if not text:
        abort(400)
    # Run TTS in async context
    import asyncio
    try:
        asyncio.run(voice.speak(text, config.VOICE_STYLE))
        return jsonify(message="Speaking")
    except Exception as e:
        return jsonify(error=str(e)), 502


@app.post("/api/wake-word")
def wake_word():
    """Toggle wake word listening."""
    if config.ENABLE_WAKE_WORD:
        asyncio.run(voice.start_wake_word())
        return jsonify(message="Wake word listening started")
    return jsonify(message="Wake word is disabled"), 200


@app.post("/api/voice/start")
def voice_start():
    """Start voice interaction."""
    asyncio.run(voice.start_listening())
    return jsonify(message="Listening")


@app.post("/api/voice/stop")
def voice_stop():
    """Stop voice interaction."""
    asyncio.run(voice.stop_listening())
    return jsonify(message="Stopped")


def _open_window():
    """Opens SOLARIS in its own app-style window (no browser tabs or address bar)."""
    time.sleep(1.2)
    url = f"http://localhost:{config.PORT}"
    try:
        subprocess.Popen(f'start "" msedge --app={url} --window-size=1280,820', shell=True)
    except Exception:
        webbrowser.open(url)


if __name__ == "__main__":
    print(f"\n  {config.NAME} v{config.VERSION} is starting at http://localhost:{config.PORT}")
    if config.PROVIDER == "gemini" and not config.GEMINI_KEY:
        print("  Note: no Gemini key yet. Commands work, but questions need the key in the .env file.")
    print("  Keep this window open while you use SOLARIS. Press Ctrl+C to stop.\n")
    if "--no-window" not in sys.argv:
        threading.Thread(target=_open_window, daemon=True).start()
    app.run(host="127.0.0.1", port=config.PORT, threaded=True)