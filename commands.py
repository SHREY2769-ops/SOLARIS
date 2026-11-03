"""Command router: understands things like "pause the wallpaper" or "open Steam" instantly,
without using the AI (so it's fast and doesn't use up your free AI limit).
Returns None when the message is a normal question for the AI."""
import re
import webbrowser
import config
import themes
import apps
import wallpaper
import media
import telemetry

SECTIONS = {
    "home": "home", "main menu": "home",
    "accessibility": "accessibility", "dashboard": "accessibility", "telemetry": "accessibility",
    "apps": "accessibility", "hardware": "accessibility",
    "wallpaper": "wallpaper", "wallpapers": "wallpaper",
    "music": "music",
    "theme": "theme", "themes": "theme", "color": "theme", "colors": "theme",
    "colour": "theme", "colours": "theme",
}
SECTION_NAMES = {"home": "home", "accessibility": "Accessibility", "wallpaper": "Wallpaper",
                 "music": "Music", "theme": "Theme"}
SITES = {"youtube": "https://www.youtube.com", "google": "https://www.google.com",
         "gmail": "https://mail.google.com", "github": "https://github.com",
         "chatgpt": "https://chatgpt.com"}

_NAME = re.escape(config.NAME.lower())


def _norm(text):
    t = text.lower().replace("'", "").replace("'", "")
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    prev = None
    while prev != t:
        prev = t
        t = re.sub(rf"^(hey |hi |ok |okay |yo )?({_NAME}|jarvis|assistant|solaris) ", "", t)
        t = re.sub(r"^(please|can you|could you|would you|will you|i want you to|i want to|go ahead and|just|now) ", "", t)
    return re.sub(r" (please|for me|now|right now|again)$", "", t)


def _say(reply, action=None):
    return {"reply": reply, "action": action}


def wants_screen(text):
    t = _norm(text)
    return bool(re.search(
        r"\b(my screen|the screen|on screen|this page|this video|this tab|this window|this website|"
        r"this error|this code|what am i (watching|looking at|reading)|look at (this|my|the)|"
        r"whats (this|that) (page|video|website|game)|read this)\b", t))


def route(text):
    t = _norm(text)
    if not t:
        return None

    # ----- go to a section -----
    if re.match(r"^(go |take me |back )?(to )?(home|the main menu|main menu)$", t):
        return _say("Back to the main menu.", {"type": "section", "view": "home"})
    m = re.match(r"^(open|show me|show|go to|take me to|switch to)( the| my)? (.+?)( section| tab| page| menu| panel)?$", t)
    if m and m.group(3) in SECTIONS:
        view = SECTIONS[m.group(3)]
        label = "the main menu" if view == "home" else f"the {SECTION_NAMES[view]} section"
        return _say(f"Opening {label}.", {"type": "section", "view": view})

    # ----- wallpaper -----
    if "wallpaper" in t and "engine" not in t:
        if re.search(r"\bunmute\b", t):
            ok, msg = wallpaper.act("unmute"), "Wallpaper sound is back on."
        elif re.search(r"\bmute\b", t):
            ok, msg = wallpaper.act("mute"), "Wallpaper muted."
        elif re.search(r"\b(pause|freeze|stop)\b", t):
            ok, msg = wallpaper.act("pause"), "Wallpaper paused."
        elif re.search(r"\b(play|resume|unpause|unfreeze|start)\b", t):
            ok, msg = wallpaper.act("play"), "Wallpaper playing."
        elif re.search(r"\b(next|change|switch|new|another|different|skip|shuffle)\b", t):
            ok, msg = wallpaper.act("next"), "Switching wallpaper."
        else:
            return None
        return _say(msg if ok else "I couldn't find Wallpaper Engine. Check the setup guide.")

    # ----- music -----
    if re.search(r"\b(whats playing|what is playing|what song|which song|now playing|current song|song name|name of (this|the) song|what am i listening)\b", t):
        n = media.now_playing()
        if n.get("active") and n.get("title"):
            by = f" by {n['artist']}" if n.get("artist") else ""
            return _say(f"This is {n['title']}{by}.", {"type": "section", "view": "music"})
        return _say("Nothing seems to be playing right now.")
    if re.search(r"\b(volume up|turn it up|louder|(increase|raise) the volume)\b", t):
        media.volume("up")
        return _say("Volume up.")
    if re.search(r"\b(volume down|turn it down|quieter|softer|(lower|decrease|reduce) the volume)\b", t):
        media.volume("down")
        return _say("Volume down.")
    if re.search(r"\b(mute|unmute)\b", t):
        media.volume("mute")
        return _say("Done.")
    music_words = r"(music|song|track|spotify|youtube|video|playing)"
    music_cmds = [
        (rf"\b(next|skip)\b.*\b{music_words}\b|^(next|skip)( it| this)?$|^play the next", "next", "Skipping."),
        (rf"\b(previous|last|go back)\b.*\b{music_words}\b|^(previous|go back)$|^play the previous", "previous", "Going back."),
        (rf"\b(pause|stop)\b.*\b{music_words}\b|^pause( it)?$", "pause", "Paused."),
        (rf"\b(play|resume|continue|unpause|start)\b.*\b{music_words}\b|^(resume|unpause|continue)$", "play", "Playing."),
    ]
    for pattern, cmd, msg in music_cmds:
        if re.search(pattern, t):
            return _say(msg if media.control(cmd) else "I couldn't find anything playing.")

    # ----- theme color -----
    if (re.search(r"\b(change|set|switch|make|turn|use|go|paint|put)\b", t)
            and re.search(r"\b(theme|colou?r|accent|arc|menu|ui|it|everything|interface)\b", t)):
        for word in t.split():
            theme_id = themes.lookup(word)
            if theme_id:
                return _say(f"Theme changed to {themes.name_of(theme_id)}.", {"type": "theme", "id": theme_id})

    # ----- how is my PC -----
    if re.search(r"\b(how is|hows)\b.*\b(pc|computer|system|laptop|cpu|ram|gpu|battery)\b|"
                 r"\bsystem (status|stats|health)\b|\b(pc|cpu|ram|memory|gpu|battery|disk) (usage|status|stats|level|health)\b|"
                 r"\bhow much (ram|memory|battery)\b", t):
        return _say(telemetry.spoken(), {"type": "section", "view": "accessibility"})

    # ----- open an app -----
    m = re.match(r"^(open|launch|start|run)( up)?( the| my)? (.+)$", t)
    if m:
        target = m.group(4)
        name = apps.launch_by_name(target)
        if name:
            return _say(f"Opening {name}.")
        if target in SITES:
            webbrowser.open(SITES[target])
            return _say(f"Opening {target.title()}.")
        return _say(f"I couldn't find an app called {target}. If it's new, open Accessibility and press Rescan.")

    return None