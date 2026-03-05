"""
Theme manager for ECRStudio — handles light/dark mode switching.
Saves user preference to a config file.
"""

import json
import os
from .constants import (
    THEME_LIGHT, THEME_DARK,
    COLORS_LIGHT, COLORS_DARK, TEXT_COLORS_DARK,
    FIELD_TYPE_COLORS, FIELD_TYPE_COLORS_DARK,
)

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".ecrstudio")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def _load_config():
    """Load user config from disk."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_config(config):
    """Save user config to disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_saved_theme():
    """Return the saved theme name ('light' or 'dark'). Defaults to 'light'."""
    config = _load_config()
    return config.get("theme", "light")


def save_theme(theme_name):
    """Save theme preference to disk."""
    config = _load_config()
    config["theme"] = theme_name
    _save_config(config)


MAX_RECENT_FILES = 8


def get_recent_files():
    """Return the list of recently opened file paths."""
    config = _load_config()
    return config.get("recent_files", [])


def add_recent_file(path):
    """Add a file path to the recent files list (most recent first)."""
    config = _load_config()
    recent = config.get("recent_files", [])
    # Remove if already present, then prepend
    abs_path = os.path.abspath(path)
    recent = [p for p in recent if p != abs_path]
    recent.insert(0, abs_path)
    config["recent_files"] = recent[:MAX_RECENT_FILES]
    _save_config(config)


class ThemeManager:
    """Manages the current theme and provides color lookups."""

    def __init__(self):
        self._theme_name = get_saved_theme()

    @property
    def is_dark(self):
        return self._theme_name == "dark"

    @property
    def name(self):
        return self._theme_name

    def toggle(self):
        """Switch between light and dark themes."""
        self._theme_name = "dark" if self._theme_name == "light" else "light"
        save_theme(self._theme_name)
        return self._theme_name

    @property
    def palette(self):
        """Return the current theme palette dict."""
        return THEME_DARK if self.is_dark else THEME_LIGHT

    @property
    def type_colors(self):
        """Return background colors per record type."""
        return COLORS_DARK if self.is_dark else COLORS_LIGHT

    @property
    def type_text_colors(self):
        """Return foreground colors per record type (only meaningful in dark mode)."""
        return TEXT_COLORS_DARK if self.is_dark else {}

    @property
    def field_type_colors(self):
        """Return colors for field type labels (Alpha/Num/Date)."""
        return FIELD_TYPE_COLORS_DARK if self.is_dark else FIELD_TYPE_COLORS
