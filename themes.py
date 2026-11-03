"""The theme colors. The screen reads this list, so there is one source of truth."""

THEMES = [
    ("cyan", "Arc Cyan", "#5fd4ff"),
    ("azure", "Azure", "#4d8dff"),
    ("violet", "Violet", "#9b7bff"),
    ("magenta", "Magenta", "#ff5fd2"),
    ("crimson", "Crimson", "#ff4d5e"),
    ("orange", "Orange", "#ff8a3d"),
    ("amber", "Amber", "#ffc84a"),
    ("lime", "Lime", "#b6f04a"),
    ("green", "Green", "#3dffa0"),
    ("teal", "Teal", "#2fe0d0"),
    ("rose", "Rose", "#ff8fb3"),
    ("silver", "Silver", "#dfe8f2"),
]

ALIASES = {
    "red": "crimson", "blue": "azure", "purple": "violet", "pink": "rose",
    "yellow": "amber", "gold": "amber", "white": "silver", "grey": "silver",
    "gray": "silver", "default": "cyan", "aqua": "teal", "turquoise": "teal",
}


def public():
    return [{"id": i, "name": n, "hex": h} for i, n, h in THEMES]


def lookup(word):
    """Turn a word like 'red' or 'violet' into a theme id (or None)."""
    word = word.lower()
    if word in ALIASES:
        return ALIASES[word]
    for theme_id, _name, _hex in THEMES:
        if theme_id == word:
            return theme_id
    return None


def name_of(theme_id):
    return next((n for i, n, _h in THEMES if i == theme_id), theme_id)
