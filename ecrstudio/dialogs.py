"""
Dialog windows for ECRStudio:
- Add line dialog
- Search & Replace dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .structures import STRUCTURES
from .parser import write_field
from .constants import ALL_TYPES, HIERARCHY, HIERARCHY_LEVEL


class AddLineDialog(tk.Toplevel):
    """Dialog to add a new ECR line."""

    def __init__(self, parent, insert_after_type=None, theme_palette=None):
        super().__init__(parent)
        self.title("Add a line")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None
        pal = theme_palette or {}
        bg = pal.get("bg", "#f0f2f5")
        fg = pal.get("text_fg", "#2c3e50")
        self.configure(bg=bg)

        tk.Label(self, text="Record type:", bg=bg, fg=fg,
                 font=("Segoe UI", 10)).pack(pady=(16, 4))

        # Filter valid child types if inserting after a known type
        valid_types = list(STRUCTURES.keys())
        if insert_after_type and insert_after_type in HIERARCHY:
            children = HIERARCHY[insert_after_type]
            if children:
                valid_types = children

        self.type_var = tk.StringVar(value=valid_types[0] if valid_types else "ECR")
        combo = ttk.Combobox(self, textvariable=self.type_var, values=valid_types,
                             state="readonly", width=15, font=("Segoe UI", 10))
        combo.pack(pady=4)

        tk.Label(self, text="A blank line with required fields will be created.",
                 bg=bg, fg=fg, font=("Segoe UI", 8, "italic")).pack(pady=8)

        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Add", command=self._on_ok,
                  bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=16, pady=4).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Cancel", command=self.destroy,
                  bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=16, pady=4).pack(side="left", padx=4)

    def _on_ok(self):
        self.result = self.type_var.get()
        self.destroy()


def create_blank_line(record_type):
    """Create a blank line for the given record type with the type field filled."""
    struct = STRUCTURES.get(record_type)
    if not struct:
        return record_type.ljust(6)

    # Determine max line length
    max_end = max(pos + length for pos, (_name, length, _t, _r) in struct.items())
    line = " " * max_end

    # Write the type field
    line = write_field(line, 1, 6, record_type.ljust(6), "Alpha")
    return line


class SearchReplaceDialog(tk.Toplevel):
    """Search and replace dialog."""

    def __init__(self, parent, on_search, on_replace, on_replace_all, theme_palette=None):
        super().__init__(parent)
        self.title("Search & Replace")
        self.geometry("480x220")
        self.resizable(False, False)
        self.transient(parent)

        self._on_search = on_search
        self._on_replace = on_replace
        self._on_replace_all = on_replace_all

        pal = theme_palette or {}
        bg = pal.get("bg", "#f0f2f5")
        fg = pal.get("text_fg", "#2c3e50")
        entry_bg = pal.get("entry_bg", "#ffffff")
        self.configure(bg=bg)

        # Search field
        tk.Label(self, text="Search:", bg=bg, fg=fg,
                 font=("Segoe UI", 10)).grid(row=0, column=0, padx=8, pady=(12, 4), sticky="w")
        self.search_var = tk.StringVar()
        tk.Entry(self, textvariable=self.search_var, font=("Consolas", 10),
                 bg=entry_bg, width=35, relief="solid", bd=1).grid(
            row=0, column=1, padx=8, pady=(12, 4), columnspan=2)

        # Replace field
        tk.Label(self, text="Replace:", bg=bg, fg=fg,
                 font=("Segoe UI", 10)).grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self.replace_var = tk.StringVar()
        tk.Entry(self, textvariable=self.replace_var, font=("Consolas", 10),
                 bg=entry_bg, width=35, relief="solid", bd=1).grid(
            row=1, column=1, padx=8, pady=4, columnspan=2)

        # Case sensitive
        self.case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Case sensitive", variable=self.case_var,
                       bg=bg, fg=fg, font=("Segoe UI", 9)).grid(
            row=2, column=1, sticky="w", padx=8, pady=4)

        # Buttons
        bf = tk.Frame(self, bg=bg)
        bf.grid(row=3, column=0, columnspan=3, pady=12)

        for text, cmd, color in [
            ("Find next",    self._do_search,      "#3498db"),
            ("Replace",      self._do_replace,     "#e67e22"),
            ("Replace all",  self._do_replace_all, "#8e44ad"),
            ("Close",        self.destroy,          "#7f8c8d"),
        ]:
            tk.Button(bf, text=text, command=cmd, bg=color, fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat",
                      padx=10, pady=3).pack(side="left", padx=3)

    def _do_search(self):
        self._on_search(self.search_var.get(), self.case_var.get())

    def _do_replace(self):
        self._on_replace(self.search_var.get(), self.replace_var.get(), self.case_var.get())

    def _do_replace_all(self):
        self._on_replace_all(self.search_var.get(), self.replace_var.get(), self.case_var.get())
