"""
ECRStudio — Main application window.

Full-featured graphical editor for ECR accounting files.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .structures import STRUCTURES
from .parser import read_field, write_field, get_record_type, read_ecr_file, save_ecr_file
from .constants import ALL_TYPES, HIERARCHY_LEVEL
from .themes import ThemeManager
from .undo import UndoManager
from .validator import validate_file, ValidationError
from .tree_builder import build_tree
from .dialogs import AddLineDialog, SearchReplaceDialog, create_blank_line
from .wizard import NewFileWizard
from .export import export_to_csv
from .diff import DiffWindow
from .widgets import FlatButton

APP_VERSION = "3.0.0"


class ECRStudioApp(tk.Tk):
    """Main application class."""

    def __init__(self):
        super().__init__()

        self.lines = []
        self.file_path = None
        self.selected_line = None
        self.modified = False
        self.field_entries = {}
        self.view_mode = "list"  # "list" or "tree"

        self.theme = ThemeManager()
        self.undo_mgr = UndoManager()
        self._font_size = 11  # Base font size (adjustable via Ctrl+/-)

        self.title(f"ECRStudio v{APP_VERSION}")
        self.geometry("1350x820")
        self.minsize(950, 650)

        self._build_menu_bar()
        self._build_ui()
        self._apply_theme()
        self._apply_zoom()
        self._bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────────
    # Menu bar
    # ──────────────────────────────────────────────

    def _build_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New (Wizard)...", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._on_close, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Add line...", command=self._add_line, accelerator="Ins")
        edit_menu.add_command(label="Duplicate line", command=self._duplicate_line, accelerator="Ctrl+D")
        edit_menu.add_command(label="Delete line", command=self._delete_line, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Move up", command=self._move_line_up, accelerator="Ctrl+Up")
        edit_menu.add_command(label="Move down", command=self._move_line_down, accelerator="Ctrl+Down")
        edit_menu.add_separator()
        edit_menu.add_command(label="Search & Replace...", command=self._open_search_replace, accelerator="Ctrl+H")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle List / Tree", command=self._toggle_view)
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Dark / Light", command=self._toggle_theme)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self._zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self._zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self._zoom_reset, accelerator="Ctrl+0")
        menubar.add_cascade(label="View", menu=view_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Validate file", command=self._validate, accelerator="F5")
        tools_menu.add_separator()
        tools_menu.add_command(label="Compare files...", command=self._compare_files)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About ECRStudio", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    # ──────────────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────────────

    def _build_ui(self):
        pal = self.theme.palette

        # Toolbar
        self.toolbar = tk.Frame(self, bg=pal["toolbar_bg"], pady=6)
        self.toolbar.pack(fill="x")

        self.lbl_title = tk.Label(self.toolbar, text=f"ECRStudio v{APP_VERSION}",
                                  bg=pal["toolbar_bg"], fg=pal["toolbar_fg"],
                                  font=("Segoe UI", 13, "bold"))
        self.lbl_title.pack(side="left", padx=12)

        self.toolbar_buttons = {}
        btn_defs = [
            ("open",     "Open .ECR",      self._open_file,      "btn_open"),
            ("new",      "New",            self._new_file,       "btn_open"),
            ("save",     "Save",           self._save,           "btn_save"),
            ("saveas",   "Save As",        self._save_as,        "btn_saveas"),
            ("add",      "+ Add",          self._add_line,       "btn_add"),
            ("dup",      "Duplicate",      self._duplicate_line, "btn_dup"),
            ("del",      "Delete",         self._delete_line,    "btn_del"),
            ("validate", "Validate",       self._validate,       "btn_validate"),
            ("view",     "List/Tree",      self._toggle_view,    "btn_open"),
            ("theme",    "Dark/Light",     self._toggle_theme,   "btn_saveas"),
        ]
        btn_fg = pal.get("btn_fg", "#ffffff")
        for key, text, cmd, color_key in btn_defs:
            b = FlatButton(self.toolbar, text=text, command=cmd,
                           bg=pal.get(color_key, "#3498db"), fg=btn_fg)
            b.pack(side="left", padx=2)
            self.toolbar_buttons[key] = (b, color_key)

        self.lbl_file = tk.Label(self.toolbar, text="No file open",
                                 bg=pal["toolbar_bg"], fg=pal["text_secondary"],
                                 font=("Segoe UI", 9))
        self.lbl_file.pack(side="left", padx=12)

        self.lbl_modified = tk.Label(self.toolbar, text="",
                                     bg=pal["toolbar_bg"], fg=pal["error_fg"],
                                     font=("Segoe UI", 9, "bold"))
        self.lbl_modified.pack(side="left")

        # Main paned window
        self.main_paned = tk.PanedWindow(self, orient="horizontal",
                                         bg=pal["sash_bg"], sashwidth=5, sashrelief="flat")
        self.main_paned.pack(fill="both", expand=True, padx=8, pady=8)

        # Left panel
        self.left_frame = tk.Frame(self.main_paned, bg=pal["bg"])
        self.main_paned.add(self.left_frame, minsize=400)

        self.lbl_lines_title = tk.Label(self.left_frame, text="ECR file lines",
                                        bg=pal["bg"], fg=pal["text_fg"],
                                        font=("Segoe UI", 10, "bold"))
        self.lbl_lines_title.pack(anchor="w", padx=6, pady=(4, 2))

        # Search / filter bar
        self.search_frame = tk.Frame(self.left_frame, bg=pal["bg"])
        self.search_frame.pack(fill="x", padx=6, pady=(0, 4))
        sf = self.search_frame

        self.lbl_search = tk.Label(sf, text="Search:", bg=pal["bg"], fg=pal["text_fg"])
        self.lbl_search.pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_lines())
        self.search_entry = tk.Entry(sf, textvariable=self.search_var,
                                     font=("Consolas", 9), relief="solid", bd=1)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=4)

        self.filter_type = tk.StringVar(value="All")
        self.filter_combo = ttk.Combobox(sf, textvariable=self.filter_type,
                                         width=9, state="readonly",
                                         values=["All"] + ALL_TYPES)
        self.filter_combo.pack(side="left")
        self.filter_type.trace_add("write", lambda *a: self._filter_lines())

        # TreeView for lines
        lf = tk.Frame(self.left_frame)
        lf.pack(fill="both", expand=True, padx=6)

        self.tree = ttk.Treeview(lf, columns=("num", "type", "preview"),
                                 show="headings", selectmode="browse")
        self.tree.heading("num", text="#", anchor="w")
        self.tree.heading("type", text="Type", anchor="w")
        self.tree.heading("preview", text="Preview", anchor="w")
        self.tree.column("num", width=45, stretch=False)
        self.tree.column("type", width=70, stretch=False)
        self.tree.column("preview", width=320)

        sb = ttk.Scrollbar(lf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Context menu
        self.ctx_menu = tk.Menu(self.tree, tearoff=0)
        self.ctx_menu.add_command(label="Add line...", command=self._add_line)
        self.ctx_menu.add_command(label="Duplicate", command=self._duplicate_line)
        self.ctx_menu.add_command(label="Delete", command=self._delete_line)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="Move up", command=self._move_line_up)
        self.ctx_menu.add_command(label="Move down", command=self._move_line_down)
        self.tree.bind("<Button-2>", self._show_context_menu)
        self.tree.bind("<Button-3>", self._show_context_menu)

        # Summary label
        self.lbl_summary = tk.Label(self.left_frame, text="",
                                    bg=pal["bg"], fg=pal["text_muted"],
                                    font=("Segoe UI", 8))
        self.lbl_summary.pack(anchor="w", padx=6, pady=2)

        # Right panel (detail)
        self.right_frame = tk.Frame(self.main_paned, bg=pal["bg"])
        self.main_paned.add(self.right_frame, minsize=480)

        self.lbl_detail_title = tk.Label(self.right_frame,
                                         text="Select a line to view its fields",
                                         bg=pal["bg"], fg=pal["text_fg"],
                                         font=("Segoe UI", 10, "bold"))
        self.lbl_detail_title.pack(anchor="w", padx=6, pady=(4, 2))

        # Scrollable detail area
        cf = tk.Frame(self.right_frame)
        cf.pack(fill="both", expand=True, padx=6)

        self.canvas = tk.Canvas(cf, bg=pal["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(cf, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.detail_frame = tk.Frame(self.canvas, bg=pal["bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")
        self.detail_frame.bind("<Configure>", self._on_detail_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Action buttons
        bf = tk.Frame(self.right_frame, bg=pal["bg"])
        bf.pack(fill="x", padx=6, pady=6)

        self.btn_apply = FlatButton(bf, text="Apply changes",
                                    command=self._apply_changes,
                                    bg=pal["btn_apply"],
                                    fg=pal.get("btn_fg", "#ffffff"),
                                    padx=12, pady=4)
        self.btn_apply.pack(side="left")

        self.btn_cancel_edit = FlatButton(bf, text="Cancel",
                                          command=self._cancel_changes,
                                          bg=pal["btn_cancel"],
                                          fg=pal.get("btn_fg", "#ffffff"),
                                          padx=12, pady=4)
        self.btn_cancel_edit.pack(side="left", padx=8)

        # Status bar
        self.status = tk.Label(self, text="Ready — Open or create an ECR file",
                               bg=pal["status_bg"], fg=pal["status_fg"],
                               font=("Segoe UI", 8), anchor="w", padx=8)
        self.status.pack(fill="x", side="bottom")

    # ──────────────────────────────────────────────
    # Theme
    # ──────────────────────────────────────────────

    def _apply_theme(self):
        pal = self.theme.palette
        type_colors = self.theme.type_colors
        type_text = self.theme.type_text_colors

        self.configure(bg=pal["bg"])
        self.toolbar.configure(bg=pal["toolbar_bg"])
        self.lbl_title.configure(bg=pal["toolbar_bg"], fg=pal["toolbar_fg"])
        self.lbl_file.configure(bg=pal["toolbar_bg"], fg=pal["text_secondary"])
        self.lbl_modified.configure(bg=pal["toolbar_bg"], fg=pal["error_fg"])

        btn_fg = pal.get("btn_fg", "#ffffff")
        for _key, (btn, color_key) in self.toolbar_buttons.items():
            btn.update_colors(pal.get(color_key, "#3498db"), btn_fg)

        self.left_frame.configure(bg=pal["bg"])
        self.right_frame.configure(bg=pal["bg"])
        self.lbl_lines_title.configure(bg=pal["bg"], fg=pal["text_fg"])
        self.search_frame.configure(bg=pal["bg"])
        self.lbl_search.configure(bg=pal["bg"], fg=pal["text_fg"])
        self.search_entry.configure(bg=pal["entry_bg"], fg=pal["text_fg"],
                                    insertbackground=pal["text_fg"])
        self.lbl_summary.configure(bg=pal["bg"], fg=pal["text_muted"])
        self.lbl_detail_title.configure(bg=pal["bg"], fg=pal["text_fg"])
        self.canvas.configure(bg=pal["bg"])
        self.detail_frame.configure(bg=pal["bg"])
        self.main_paned.configure(bg=pal["sash_bg"])
        self.status.configure(bg=pal["status_bg"], fg=pal["status_fg"])

        self.btn_apply.update_colors(pal["btn_apply"], btn_fg)
        self.btn_cancel_edit.update_colors(pal["btn_cancel"], btn_fg)

        # Update Treeview tags
        for t in ALL_TYPES:
            bg_color = type_colors.get(t, pal["bg"])
            fg_color = type_text.get(t, "#000000") if self.theme.is_dark else "#000000"
            self.tree.tag_configure(t, background=bg_color, foreground=fg_color)

        # Refresh detail if a line is selected
        if self.selected_line is not None:
            self._show_detail(self.selected_line)

    def _toggle_theme(self):
        self.theme.toggle()
        self._apply_theme()
        self._set_status(f"Theme switched to {self.theme.name}")

    # ──────────────────────────────────────────────
    # Zoom
    # ──────────────────────────────────────────────

    def _zoom_in(self):
        if self._font_size < 20:
            self._font_size += 1
            self._apply_zoom()

    def _zoom_out(self):
        if self._font_size > 8:
            self._font_size -= 1
            self._apply_zoom()

    def _zoom_reset(self):
        self._font_size = 11
        self._apply_zoom()

    def _apply_zoom(self):
        """Reapply fonts at current zoom level and refresh detail."""
        fs = self._font_size
        fs_small = max(fs - 2, 7)
        fs_mono = max(fs - 1, 8)

        # Update treeview row height via style
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", fs_small), rowheight=int(fs * 1.8))
        style.configure("Treeview.Heading", font=("Segoe UI", fs_small, "bold"))

        # Update fixed labels
        self.lbl_title.configure(font=("Segoe UI", fs + 2, "bold"))
        self.lbl_lines_title.configure(font=("Segoe UI", fs, "bold"))
        self.lbl_detail_title.configure(font=("Segoe UI", fs, "bold"))
        self.lbl_summary.configure(font=("Segoe UI", fs_small))
        self.lbl_file.configure(font=("Segoe UI", fs_small))
        self.status.configure(font=("Segoe UI", fs_small))
        self.search_entry.configure(font=("Consolas", fs_mono))

        # Refresh detail panel if a line is selected
        if self.selected_line is not None:
            self._show_detail(self.selected_line)

        self._set_status(f"Zoom: {fs}pt")

    # ──────────────────────────────────────────────
    # Keyboard shortcuts
    # ──────────────────────────────────────────────

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._save())
        self.bind("<Control-Shift-S>", lambda e: self._save_as())
        self.bind("<Control-n>", lambda e: self._new_file())
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-y>", lambda e: self._redo())
        self.bind("<Control-d>", lambda e: self._duplicate_line())
        self.bind("<Control-h>", lambda e: self._open_search_replace())
        self.bind("<Control-q>", lambda e: self._on_close())
        self.bind("<Delete>", lambda e: self._delete_line())
        self.bind("<Insert>", lambda e: self._add_line())
        self.bind("<Control-Up>", lambda e: self._move_line_up())
        self.bind("<Control-Down>", lambda e: self._move_line_down())
        self.bind("<F5>", lambda e: self._validate())
        # Zoom shortcuts
        self.bind("<Control-plus>", lambda e: self._zoom_in())
        self.bind("<Control-equal>", lambda e: self._zoom_in())
        self.bind("<Control-minus>", lambda e: self._zoom_out())
        self.bind("<Control-0>", lambda e: self._zoom_reset())

    # ──────────────────────────────────────────────
    # Canvas scrolling
    # ──────────────────────────────────────────────

    def _on_detail_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # macOS uses event.delta differently
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

    # ──────────────────────────────────────────────
    # File operations
    # ──────────────────────────────────────────────

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open ECR file",
            filetypes=[("ECR files", "*.ecr *.ECR"), ("All", "*.*")])
        if not path:
            return
        try:
            self.lines = read_ecr_file(path)
            self.file_path = path
            self.modified = False
            self.undo_mgr.clear()
            self.lbl_modified.config(text="")
            name = os.path.basename(path)
            self.lbl_file.config(text=name, fg=self.theme.palette["success_fg"])
            self.title(f"ECRStudio — {name}")
            self._refresh_list()
            self._set_status(f"Opened: {path}  ({len(self.lines)} lines)")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file:\n{e}")

    def _new_file(self):
        if self.modified and not self._confirm_discard():
            return
        wiz = NewFileWizard(self, theme_palette=self.theme.palette)
        self.wait_window(wiz)
        if wiz.result:
            self.lines = wiz.result
            self.file_path = None
            self.modified = True
            self.undo_mgr.clear()
            self.lbl_modified.config(text="*")
            self.lbl_file.config(text="New file (unsaved)")
            self.title(f"ECRStudio — New file *")
            self._refresh_list()
            self._set_status("New file created via wizard")

    def _save(self):
        if not self.lines:
            messagebox.showwarning("Warning", "No file open.")
            return
        if not self.file_path:
            self._save_as()
            return
        try:
            save_ecr_file(self.file_path, self.lines)
            self.modified = False
            self.lbl_modified.config(text="")
            name = os.path.basename(self.file_path)
            self.title(f"ECRStudio — {name}")
            self._set_status(f"Saved: {self.file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save:\n{e}")

    def _save_as(self):
        if not self.lines:
            messagebox.showwarning("Warning", "No file open.")
            return
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".ECR",
            filetypes=[("ECR files", "*.ecr *.ECR"), ("All", "*.*")])
        if not path:
            return
        try:
            save_ecr_file(path, self.lines)
            self.file_path = path
            self.modified = False
            self.lbl_modified.config(text="")
            name = os.path.basename(path)
            self.lbl_file.config(text=name)
            self.title(f"ECRStudio — {name}")
            self._set_status(f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save:\n{e}")

    def _export_csv(self):
        if not self.lines:
            messagebox.showwarning("Warning", "No file open.")
            return
        path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All", "*.*")])
        if not path:
            return
        try:
            export_to_csv(self.lines, path)
            self._set_status(f"Exported to: {path}")
            messagebox.showinfo("Export", f"CSV exported:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot export:\n{e}")

    def _on_close(self):
        if self.modified:
            ans = messagebox.askyesnocancel(
                "Unsaved changes",
                "You have unsaved changes. Save before quitting?")
            if ans is None:
                return
            if ans:
                self._save()
        self.destroy()

    def _confirm_discard(self):
        return messagebox.askyesno(
            "Unsaved changes",
            "Discard current unsaved changes?")

    # ──────────────────────────────────────────────
    # List / Tree view
    # ──────────────────────────────────────────────

    def _refresh_list(self):
        if self.view_mode == "tree":
            self._fill_tree_view()
        else:
            self._fill_flat_list()

    def _fill_flat_list(self):
        self.tree.delete(*self.tree.get_children())
        # Reconfigure for flat mode
        self.tree["show"] = "headings"

        counters = {}
        for i, line in enumerate(self.lines):
            t = get_record_type(line)
            counters[t] = counters.get(t, 0) + 1
            preview = self._make_preview(line, t)
            tag = t if t in self.theme.type_colors else ""
            self.tree.insert("", "end", iid=str(i),
                             values=(i + 1, t, preview), tags=(tag,))

        summary = "  ".join(f"{t}:{n}" for t, n in sorted(counters.items()))
        self.lbl_summary.config(text=f"Total: {len(self.lines)} lines  |  {summary}")

    def _fill_tree_view(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["show"] = "tree headings"

        roots = build_tree(self.lines)
        self._insert_tree_nodes(roots, parent="")

        counters = {}
        for line in self.lines:
            t = get_record_type(line)
            counters[t] = counters.get(t, 0) + 1
        summary = "  ".join(f"{t}:{n}" for t, n in sorted(counters.items()))
        self.lbl_summary.config(text=f"Total: {len(self.lines)} lines  |  {summary}")

    def _insert_tree_nodes(self, nodes, parent):
        for node in nodes:
            tag = node.record_type if node.record_type in self.theme.type_colors else ""
            iid = str(node.line_index)
            self.tree.insert(parent, "end", iid=iid,
                             text=node.label,
                             values=(node.line_index + 1, node.record_type, node.label),
                             tags=(tag,), open=True)
            if node.children:
                self._insert_tree_nodes(node.children, parent=iid)

    def _toggle_view(self):
        self.view_mode = "tree" if self.view_mode == "list" else "list"
        self._refresh_list()
        self._set_status(f"View: {self.view_mode}")

    def _filter_lines(self):
        if not self.lines:
            return
        text = self.search_var.get().lower()
        filter_type = self.filter_type.get()

        self.tree.delete(*self.tree.get_children())
        self.tree["show"] = "headings"

        for i, line in enumerate(self.lines):
            t = get_record_type(line)
            if filter_type != "All" and t != filter_type:
                continue
            preview = self._make_preview(line, t)
            if text and text not in line.lower() and text not in preview.lower():
                continue
            tag = t if t in self.theme.type_colors else ""
            self.tree.insert("", "end", iid=str(i),
                             values=(i + 1, t, preview), tags=(tag,))

    def _make_preview(self, line, rec_type):
        try:
            if rec_type == "CPT":
                return f"{read_field(line, 7, 10).strip()}  {read_field(line, 17, 30).strip()}"
            elif rec_type == "ECR":
                return f"{read_field(line, 7, 2).strip()} {read_field(line, 9, 8).strip()}  {read_field(line, 25, 30).strip()}"
            elif rec_type == "MVT":
                return f"{read_field(line, 7, 10).strip()}  {read_field(line, 17, 30).strip()}  D:{read_field(line, 47, 13).strip()} C:{read_field(line, 60, 13).strip()}"
            elif rec_type == "DOS":
                return read_field(line, 15, 30).strip()
            elif rec_type == "JOU":
                return f"{read_field(line, 7, 2).strip()}  {read_field(line, 9, 30).strip()}"
            elif rec_type == "TVA":
                return f"{read_field(line, 7, 2).strip()}  {read_field(line, 9, 30).strip()}"
            elif rec_type == "TIERS":
                return read_field(line, 7, 30).strip()
            elif rec_type == "ECHMVT":
                return f"TTC:{read_field(line, 7, 13).strip()}  Ech:{read_field(line, 30, 8).strip()}"
            elif rec_type == "ANAMVT":
                return f"{read_field(line, 7, 6).strip()}  {read_field(line, 15, 40).strip()}"
            else:
                return line[6:56].strip()
        except Exception:
            return line[:50]

    # ──────────────────────────────────────────────
    # Detail panel
    # ──────────────────────────────────────────────

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.selected_line = idx
        self._show_detail(idx)

    def _show_detail(self, idx):
        line = self.lines[idx]
        rec_type = get_record_type(line)
        struct = STRUCTURES.get(rec_type)
        pal = self.theme.palette
        ft_colors = self.theme.field_type_colors

        for w in self.detail_frame.winfo_children():
            w.destroy()
        self.field_entries.clear()

        self.lbl_detail_title.config(
            text=f"Line {idx + 1}  —  Type: {rec_type}  —  Length: {len(line)} chars")

        fs = self._font_size
        fs_small = max(fs - 2, 7)
        fs_mono = max(fs - 1, 8)
        font_hdr = ("Segoe UI", fs_small, "bold")
        font_cell = ("Segoe UI", fs_small)
        font_mono = ("Consolas", fs_mono)

        if struct is None:
            tk.Label(self.detail_frame, text=f"Type '{rec_type}': no structure defined",
                     bg=pal["bg"], fg=pal["text_fg"],
                     font=("Segoe UI", fs_small, "italic")).grid(
                row=0, column=0, columnspan=6, sticky="w", padx=6, pady=4)
            tk.Label(self.detail_frame, text=line, bg=pal["entry_alt_bg"],
                     fg=pal["text_fg"], font=font_mono, relief="solid", bd=1,
                     wraplength=560, justify="left").grid(
                row=1, column=0, columnspan=6, sticky="w", padx=6)
            return

        # Headers: Pos, Len, Type, Req, Field, Value
        # Compact widths for Pos/Len/Type/Req; Field and Value get more space
        headers = [("Pos", 3), ("Len", 3), ("Type", 5), ("Req", 3), ("Field", 22), ("Value", 0)]
        for col, (txt, w) in enumerate(headers):
            lbl = tk.Label(self.detail_frame, text=txt, bg=pal["header_bg"], fg=pal["header_fg"],
                           font=font_hdr, anchor="w", padx=4, pady=2)
            if w > 0:
                lbl.configure(width=w)
            lbl.grid(row=0, column=col, sticky="ew", padx=1, pady=1)

        for row, (position, (name, length, field_type, required)) in enumerate(
                sorted(struct.items()), start=1):
            value = read_field(line, position, length)
            bg = pal["entry_bg"] if row % 2 == 0 else pal["entry_alt_bg"]
            fg = pal["text_fg"]

            tk.Label(self.detail_frame, text=str(position), bg=bg, fg=fg,
                     font=font_mono, anchor="e", width=3, padx=2).grid(
                row=row, column=0, sticky="ew", padx=1, pady=1)

            tk.Label(self.detail_frame, text=str(length), bg=bg, fg=fg,
                     font=font_mono, anchor="e", width=3, padx=2).grid(
                row=row, column=1, sticky="ew", padx=1, pady=1)

            tk.Label(self.detail_frame, text=field_type, bg=bg,
                     fg=ft_colors.get(field_type, fg),
                     font=("Segoe UI", fs_small, "bold"), width=5, padx=2).grid(
                row=row, column=2, sticky="ew", padx=1, pady=1)

            # Required indicator
            req_text = "OBL" if required else ""
            req_fg = pal["error_fg"] if required else pal["text_muted"]
            tk.Label(self.detail_frame, text=req_text, bg=bg, fg=req_fg,
                     font=("Segoe UI", fs_small, "bold"), width=3, padx=2).grid(
                row=row, column=3, sticky="ew", padx=1, pady=1)

            tk.Label(self.detail_frame, text=name, bg=bg, fg=fg,
                     font=font_cell, anchor="w", padx=4).grid(
                row=row, column=4, sticky="ew", padx=1, pady=1)

            entry_bg = bg
            # Highlight empty required fields in red
            if required and not value.strip():
                entry_bg = "#ffcccc" if not self.theme.is_dark else "#4d1a1a"

            entry = tk.Entry(self.detail_frame, font=font_mono,
                             relief="solid", bd=1, bg=entry_bg, fg=fg)
            entry.insert(0, value)
            entry.grid(row=row, column=5, sticky="ew", padx=2, pady=1)
            self.field_entries[position] = (entry, length, field_type)

        self.detail_frame.columnconfigure(5, weight=1)

    def _apply_changes(self):
        if self.selected_line is None:
            messagebox.showwarning("Warning", "No line selected.")
            return

        idx = self.selected_line
        self.undo_mgr.save_state(self.lines)

        line = self.lines[idx]
        rec_type = get_record_type(line)
        struct = STRUCTURES.get(rec_type)
        if struct is None:
            messagebox.showinfo("Info", "This line type is not editable.")
            return

        for position, (entry, length, field_type) in self.field_entries.items():
            line = write_field(line, position, length, entry.get(), field_type)

        self.lines[idx] = line
        self._mark_modified()

        # Update preview in tree
        new_type = get_record_type(line)
        preview = self._make_preview(line, new_type)
        try:
            self.tree.item(str(idx), values=(idx + 1, new_type, preview))
        except tk.TclError:
            pass

        self._set_status(f"Line {idx + 1} modified")

    def _cancel_changes(self):
        if self.selected_line is not None:
            self._show_detail(self.selected_line)
            self._set_status("Changes cancelled")

    # ──────────────────────────────────────────────
    # Line operations (CRUD)
    # ──────────────────────────────────────────────

    def _add_line(self):
        if not self.lines:
            # If no file, force new file first
            self._new_file()
            return

        # Determine context for valid child types
        parent_type = None
        insert_idx = len(self.lines)
        if self.selected_line is not None:
            parent_type = get_record_type(self.lines[self.selected_line])
            insert_idx = self.selected_line + 1

        dlg = AddLineDialog(self, insert_after_type=parent_type,
                            theme_palette=self.theme.palette)
        self.wait_window(dlg)

        if dlg.result:
            self.undo_mgr.save_state(self.lines)
            new_line = create_blank_line(dlg.result)
            self.lines.insert(insert_idx, new_line)
            self._mark_modified()
            self._refresh_list()
            self._set_status(f"Added {dlg.result} line at position {insert_idx + 1}")

    def _duplicate_line(self):
        if self.selected_line is None:
            return
        self.undo_mgr.save_state(self.lines)
        idx = self.selected_line
        self.lines.insert(idx + 1, self.lines[idx])
        self._mark_modified()
        self._refresh_list()
        self._set_status(f"Duplicated line {idx + 1}")

    def _delete_line(self):
        if self.selected_line is None:
            return
        idx = self.selected_line
        rec_type = get_record_type(self.lines[idx])
        if not messagebox.askyesno("Confirm deletion",
                                   f"Delete line {idx + 1} ({rec_type})?"):
            return
        self.undo_mgr.save_state(self.lines)
        self.lines.pop(idx)
        self.selected_line = None
        self._mark_modified()
        self._refresh_list()
        self._set_status(f"Deleted line {idx + 1}")

    def _move_line_up(self):
        if self.selected_line is None or self.selected_line == 0:
            return
        self.undo_mgr.save_state(self.lines)
        idx = self.selected_line
        self.lines[idx - 1], self.lines[idx] = self.lines[idx], self.lines[idx - 1]
        self.selected_line = idx - 1
        self._mark_modified()
        self._refresh_list()
        self._select_line(idx - 1)

    def _move_line_down(self):
        if self.selected_line is None or self.selected_line >= len(self.lines) - 1:
            return
        self.undo_mgr.save_state(self.lines)
        idx = self.selected_line
        self.lines[idx], self.lines[idx + 1] = self.lines[idx + 1], self.lines[idx]
        self.selected_line = idx + 1
        self._mark_modified()
        self._refresh_list()
        self._select_line(idx + 1)

    def _select_line(self, idx):
        iid = str(idx)
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.see(iid)

    # ──────────────────────────────────────────────
    # Undo / Redo
    # ──────────────────────────────────────────────

    def _undo(self):
        restored = self.undo_mgr.undo(self.lines)
        if restored is None:
            self._set_status("Nothing to undo")
            return
        self.lines = restored
        self._mark_modified()
        self._refresh_list()
        self._set_status("Undo")

    def _redo(self):
        restored = self.undo_mgr.redo(self.lines)
        if restored is None:
            self._set_status("Nothing to redo")
            return
        self.lines = restored
        self._mark_modified()
        self._refresh_list()
        self._set_status("Redo")

    # ──────────────────────────────────────────────
    # Validation
    # ──────────────────────────────────────────────

    def _validate(self):
        if not self.lines:
            messagebox.showwarning("Warning", "No file open.")
            return

        errors = validate_file(self.lines)
        if not errors:
            messagebox.showinfo("Validation", "No issues found! File is valid.")
            self._set_status("Validation: OK")
            return

        # Show validation results in a window
        win = tk.Toplevel(self)
        win.title("Validation results")
        win.geometry("700x450")
        win.transient(self)

        pal = self.theme.palette
        win.configure(bg=pal["bg"])

        n_err = sum(1 for e in errors if e.severity == ValidationError.ERROR)
        n_warn = sum(1 for e in errors if e.severity == ValidationError.WARNING)

        tk.Label(win, text=f"Found {n_err} error(s) and {n_warn} warning(s)",
                 bg=pal["bg"], fg=pal["text_fg"],
                 font=("Segoe UI", 11, "bold")).pack(pady=(8, 4))

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=8, pady=4)

        tree = ttk.Treeview(frame, columns=("sev", "line", "message"),
                            show="headings", selectmode="browse")
        tree.heading("sev", text="Severity")
        tree.heading("line", text="Line")
        tree.heading("message", text="Message")
        tree.column("sev", width=70, stretch=False)
        tree.column("line", width=60, stretch=False)
        tree.column("message", width=500)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        tree.tag_configure("error", background="#f8d7da")
        tree.tag_configure("warning", background="#fff3cd")

        for i, err in enumerate(errors):
            line_num = str(err.line_index + 1) if err.line_index is not None else "-"
            tree.insert("", "end", iid=str(i),
                        values=(err.severity.upper(), line_num, err.message),
                        tags=(err.severity,))

        def on_dblclick(event):
            sel = tree.selection()
            if not sel:
                return
            err = errors[int(sel[0])]
            if err.line_index is not None:
                self._select_line(err.line_index)
                self.selected_line = err.line_index
                self._show_detail(err.line_index)
                win.lift()

        tree.bind("<Double-1>", on_dblclick)

        self._set_status(f"Validation: {n_err} error(s), {n_warn} warning(s)")

    # ──────────────────────────────────────────────
    # Search & Replace
    # ──────────────────────────────────────────────

    def _open_search_replace(self):
        if not self.lines:
            return
        self._search_index = -1
        SearchReplaceDialog(
            self,
            on_search=self._do_search,
            on_replace=self._do_replace,
            on_replace_all=self._do_replace_all,
            theme_palette=self.theme.palette
        )

    def _do_search(self, search_text, case_sensitive):
        if not search_text:
            return
        start = self._search_index + 1 if hasattr(self, '_search_index') else 0
        for i in range(start, len(self.lines)):
            line = self.lines[i]
            haystack = line if case_sensitive else line.lower()
            needle = search_text if case_sensitive else search_text.lower()
            if needle in haystack:
                self._search_index = i
                self._select_line(i)
                self.selected_line = i
                self._show_detail(i)
                return
        self._search_index = -1
        messagebox.showinfo("Search", "No more matches found.")

    def _do_replace(self, search_text, replace_text, case_sensitive):
        if not search_text or self.selected_line is None:
            return
        self.undo_mgr.save_state(self.lines)
        line = self.lines[self.selected_line]
        if case_sensitive:
            self.lines[self.selected_line] = line.replace(search_text, replace_text, 1)
        else:
            idx = line.lower().find(search_text.lower())
            if idx >= 0:
                self.lines[self.selected_line] = line[:idx] + replace_text + line[idx + len(search_text):]
        self._mark_modified()
        self._refresh_list()
        self._show_detail(self.selected_line)

    def _do_replace_all(self, search_text, replace_text, case_sensitive):
        if not search_text:
            return
        self.undo_mgr.save_state(self.lines)
        count = 0
        for i, line in enumerate(self.lines):
            if case_sensitive:
                if search_text in line:
                    self.lines[i] = line.replace(search_text, replace_text)
                    count += 1
            else:
                if search_text.lower() in line.lower():
                    # Simple case-insensitive replace
                    import re
                    self.lines[i] = re.sub(re.escape(search_text), replace_text,
                                           line, flags=re.IGNORECASE)
                    count += 1
        self._mark_modified()
        self._refresh_list()
        messagebox.showinfo("Replace All", f"Replaced in {count} line(s).")

    # ──────────────────────────────────────────────
    # Compare files
    # ──────────────────────────────────────────────

    def _compare_files(self):
        if not self.lines:
            messagebox.showwarning("Warning", "Open a file first.")
            return
        DiffWindow(self, self.lines,
                   self.file_path or "Current file",
                   theme_palette=self.theme.palette)

    # ──────────────────────────────────────────────
    # Context menu
    # ──────────────────────────────────────────────

    def _show_context_menu(self, event):
        try:
            iid = self.tree.identify_row(event.y)
            if iid:
                self.tree.selection_set(iid)
                self.selected_line = int(iid)
            self.ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx_menu.grab_release()

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def _mark_modified(self):
        self.modified = True
        self.lbl_modified.config(text="*")
        name = os.path.basename(self.file_path) if self.file_path else "New file"
        self.title(f"ECRStudio — {name} *")

    def _set_status(self, text):
        self.status.config(text=text)

    def _show_about(self):
        messagebox.showinfo(
            "About ECRStudio",
            f"ECRStudio v{APP_VERSION}\n\n"
            "Graphical editor for ECR accounting files\n\n"
            "Author: Geoffrey FLEUR @ Bobbee\n"
            "License: MIT"
        )


def main():
    app = ECRStudioApp()
    app.mainloop()
