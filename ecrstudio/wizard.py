"""
New file creation wizard for ECRStudio.

Multi-step dialog to create a valid ECR file from scratch with:
1. VER (header)
2. DOS (accounting folder)
3. EXO (fiscal year)
"""

import tkinter as tk
from tkinter import ttk
from .parser import write_field


class NewFileWizard(tk.Toplevel):
    """Multi-step wizard dialog for creating a new ECR file."""

    def __init__(self, parent, theme_palette=None):
        super().__init__(parent)
        self.title("New ECR file — Wizard")
        self.geometry("520x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None  # Will be set to a list of lines if completed
        self._step = 0
        self._data = {}

        pal = theme_palette or {}
        self._bg = pal.get("bg", "#f0f2f5")
        self._fg = pal.get("text_fg", "#2c3e50")
        self._entry_bg = pal.get("entry_bg", "#ffffff")
        self.configure(bg=self._bg)

        # Title bar
        self._title_label = tk.Label(self, text="", bg=self._bg, fg=self._fg,
                                     font=("Segoe UI", 12, "bold"))
        self._title_label.pack(pady=(16, 8))

        # Step indicator
        self._step_label = tk.Label(self, text="", bg=self._bg, fg="#7f8c8d",
                                    font=("Segoe UI", 9))
        self._step_label.pack()

        # Content frame
        self._content = tk.Frame(self, bg=self._bg)
        self._content.pack(fill="both", expand=True, padx=24, pady=8)

        # Navigation buttons
        nav = tk.Frame(self, bg=self._bg)
        nav.pack(fill="x", padx=24, pady=(0, 16))

        self._btn_back = tk.Button(nav, text="< Back", command=self._back,
                                   bg="#95a5a6", fg="white", font=("Segoe UI", 9, "bold"),
                                   relief="flat", padx=12, pady=4)
        self._btn_back.pack(side="left")

        self._btn_cancel = tk.Button(nav, text="Cancel", command=self.destroy,
                                     bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"),
                                     relief="flat", padx=12, pady=4)
        self._btn_cancel.pack(side="left", padx=8)

        self._btn_next = tk.Button(nav, text="Next >", command=self._next,
                                   bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"),
                                   relief="flat", padx=12, pady=4)
        self._btn_next.pack(side="right")

        self._entries = {}
        self._show_step()

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()
        self._entries.clear()

    def _add_field(self, label, key, default="", width=30):
        row = len(self._entries)
        tk.Label(self._content, text=label, bg=self._bg, fg=self._fg,
                 font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=4)
        var = tk.StringVar(value=self._data.get(key, default))
        entry = tk.Entry(self._content, textvariable=var, font=("Consolas", 10),
                         bg=self._entry_bg, width=width, relief="solid", bd=1)
        entry.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=4)
        self._entries[key] = var
        return var

    def _show_step(self):
        self._clear_content()
        steps = [
            ("Step 1/3 — File header (VER)", self._step_ver),
            ("Step 2/3 — Accounting folder (DOS)", self._step_dos),
            ("Step 3/3 — Fiscal year (EXO)", self._step_exo),
        ]

        title, builder = steps[self._step]
        self._title_label.config(text=title)
        self._step_label.config(text=f"Step {self._step + 1} of {len(steps)}")
        builder()

        self._btn_back.config(state="normal" if self._step > 0 else "disabled")
        if self._step == len(steps) - 1:
            self._btn_next.config(text="Create", bg="#27ae60")
        else:
            self._btn_next.config(text="Next >", bg="#3498db")

    def _step_ver(self):
        self._add_field("File label:", "ver_libelle", "New ECR file", 30)
        self._add_field("Min ISACOMPTA version:", "ver_version", "0200000", 10)

    def _step_dos(self):
        self._add_field("Folder code (8 chars max):", "dos_code", "", 10)
        self._add_field("Folder label:", "dos_libelle", "", 30)
        self._add_field("Account size (2 digits):", "dos_taille_comptes", "10", 5)

    def _step_exo(self):
        self._add_field("Start date (jjmmaaaa):", "exo_debut", "01012025", 10)
        self._add_field("End date (jjmmaaaa):", "exo_fin", "31122025", 10)
        self._add_field("Currency (3 chars):", "exo_devise", "EUR", 5)

    def _collect_data(self):
        for key, var in self._entries.items():
            self._data[key] = var.get()

    def _back(self):
        if self._step > 0:
            self._collect_data()
            self._step -= 1
            self._show_step()

    def _next(self):
        self._collect_data()
        if self._step < 2:
            self._step += 1
            self._show_step()
        else:
            self._create_file()

    def _create_file(self):
        lines = []

        # VER line
        ver = " " * 50
        ver = write_field(ver, 1, 6, "VER   ", "Alpha")
        ver = write_field(ver, 7, 7, self._data.get("ver_version", "0200000"), "Num")
        ver = write_field(ver, 14, 4, "0000", "Num")
        ver = write_field(ver, 18, 1, "0", "Num")
        ver = write_field(ver, 19, 30, self._data.get("ver_libelle", ""), "Alpha")
        ver = write_field(ver, 49, 1, "0", "Num")
        lines.append(ver)

        # DOS line
        dos = " " * 86
        dos = write_field(dos, 1, 6, "DOS   ", "Alpha")
        dos = write_field(dos, 7, 8, self._data.get("dos_code", ""), "Alpha")
        dos = write_field(dos, 15, 30, self._data.get("dos_libelle", ""), "Alpha")
        dos = write_field(dos, 59, 2, self._data.get("dos_taille_comptes", "10"), "Num")
        lines.append(dos)

        # EXO line
        exo = " " * 48
        exo = write_field(exo, 1, 6, "EXO   ", "Alpha")
        exo = write_field(exo, 7, 8, self._data.get("exo_debut", "01012025"), "Date")
        exo = write_field(exo, 15, 8, self._data.get("exo_fin", "31122025"), "Date")
        exo = write_field(exo, 36, 3, self._data.get("exo_devise", "EUR"), "Alpha")
        lines.append(exo)

        self.result = lines
        self.destroy()
