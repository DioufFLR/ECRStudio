"""
Reusable custom widgets for ECRStudio.

FlatButton: A cross-platform button that properly respects bg/fg colors.
macOS Aqua ignores bg/fg on tk.Button, so we use Frame+Label with click bindings.
"""

import tkinter as tk


class FlatButton(tk.Frame):
    """A flat button widget that respects bg/fg on all platforms."""

    def __init__(self, parent, text="", command=None, bg="#3498db", fg="#ffffff",
                 font=("Segoe UI", 9, "bold"), padx=8, pady=3, **kwargs):
        super().__init__(parent, bg=bg, cursor="hand2", bd=0, highlightthickness=0)
        self._command = command
        self._bg = bg
        self._fg = fg

        self._label = tk.Label(self, text=text, bg=bg, fg=fg, font=font,
                               padx=padx, pady=pady, cursor="hand2")
        self._label.pack(fill="both", expand=True)

        for widget in (self, self._label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        if not getattr(self, '_enabled', True):
            return
        hover = self._hover_color()
        self.configure(bg=hover)
        self._label.configure(bg=hover)

    def _on_leave(self, event):
        if not getattr(self, '_enabled', True):
            return
        self.configure(bg=self._bg)
        self._label.configure(bg=self._bg)

    def _hover_color(self):
        """Create a slightly lighter version of the bg color for hover."""
        try:
            r, g, b = self.winfo_rgb(self._bg)
            r = min(65535, int(r * 1.15))
            g = min(65535, int(g * 1.15))
            b = min(65535, int(b * 1.15))
            return f"#{r >> 8:02x}{g >> 8:02x}{b >> 8:02x}"
        except Exception:
            return self._bg

    def _dim_color(self):
        """Create a muted/greyed version of the bg color for disabled state."""
        try:
            r, g, b = self.winfo_rgb(self._bg)
            # Desaturate and darken: blend towards grey
            grey = (r + g + b) // 3
            r = (r + grey) // 2
            g = (g + grey) // 2
            b = (b + grey) // 2
            # Darken slightly
            r = int(r * 0.6)
            g = int(g * 0.6)
            b = int(b * 0.6)
            return f"#{r >> 8:02x}{g >> 8:02x}{b >> 8:02x}"
        except Exception:
            return "#555555"

    def set_enabled(self, enabled):
        """Enable or disable the button."""
        self._enabled = enabled
        if enabled:
            self.configure(bg=self._bg, cursor="hand2")
            self._label.configure(bg=self._bg, fg=self._fg, cursor="hand2")
        else:
            dim = self._dim_color()
            self.configure(bg=dim, cursor="arrow")
            self._label.configure(bg=dim, fg="#aaaaaa", cursor="arrow")

    def _on_click(self, event):
        if getattr(self, '_enabled', True) and self._command:
            self._command()

    def update_colors(self, bg, fg):
        """Update button colors (for theme switching)."""
        self._bg = bg
        self._fg = fg
        self.configure(bg=bg)
        self._label.configure(bg=bg, fg=fg)
