"""
Side-by-side file comparison for ECR files.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from .parser import read_ecr_file, get_record_type, read_field
from .structures import STRUCTURES
from .widgets import FlatButton


class DiffResult:
    """Represents a comparison result for a single line pair."""
    EQUAL = "equal"
    MODIFIED = "modified"
    ADDED = "added"
    REMOVED = "removed"

    def __init__(self, status, left_index=None, right_index=None,
                 left_line=None, right_line=None, changed_fields=None):
        self.status = status
        self.left_index = left_index
        self.right_index = right_index
        self.left_line = left_line
        self.right_line = right_line
        self.changed_fields = changed_fields or []


def compare_files(lines_a, lines_b):
    """Compare two lists of ECR lines.

    Uses a simple line-by-line comparison with field-level diff for matching types.
    Returns a list of DiffResult.
    """
    results = []
    max_len = max(len(lines_a), len(lines_b))

    for i in range(max_len):
        if i >= len(lines_a):
            results.append(DiffResult(DiffResult.ADDED,
                                      right_index=i, right_line=lines_b[i]))
        elif i >= len(lines_b):
            results.append(DiffResult(DiffResult.REMOVED,
                                      left_index=i, left_line=lines_a[i]))
        elif lines_a[i] == lines_b[i]:
            results.append(DiffResult(DiffResult.EQUAL,
                                      left_index=i, right_index=i,
                                      left_line=lines_a[i], right_line=lines_b[i]))
        else:
            changed = _find_changed_fields(lines_a[i], lines_b[i])
            results.append(DiffResult(DiffResult.MODIFIED,
                                      left_index=i, right_index=i,
                                      left_line=lines_a[i], right_line=lines_b[i],
                                      changed_fields=changed))

    return results


def _find_changed_fields(line_a, line_b):
    """Find which fields differ between two lines of the same type."""
    type_a = get_record_type(line_a)
    type_b = get_record_type(line_b)

    if type_a != type_b:
        return [("Type", type_a, type_b)]

    struct = STRUCTURES.get(type_a)
    if not struct:
        return [("Raw", line_a[:50], line_b[:50])]

    changes = []
    for pos, (name, length, _ftype, _req) in sorted(struct.items()):
        val_a = read_field(line_a, pos, length)
        val_b = read_field(line_b, pos, length)
        if val_a != val_b:
            changes.append((name, val_a.strip(), val_b.strip()))

    return changes


class DiffWindow(tk.Toplevel):
    """Side-by-side comparison window."""

    def __init__(self, parent, lines_left, path_left, theme_palette=None):
        super().__init__(parent)
        self.title("ECR File Comparison")
        self.geometry("1200x700")
        self.minsize(800, 400)

        self._lines_left = lines_left
        self._path_left = path_left
        self._lines_right = None
        self._diff_results = []
        self._diff_index = -1

        pal = theme_palette or {}
        bg = pal.get("bg", "#f0f2f5")
        fg = pal.get("text_fg", "#2c3e50")
        self.configure(bg=bg)

        # Toolbar
        toolbar = tk.Frame(self, bg=pal.get("toolbar_bg", "#2c3e50"), pady=6)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="File comparison",
                 bg=pal.get("toolbar_bg", "#2c3e50"),
                 fg=pal.get("toolbar_fg", "white"),
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=12)

        FlatButton(toolbar, text="Open file to compare...",
                   command=self._open_right_file,
                   bg="#3498db", fg="white",
                   font=("Segoe UI", 9, "bold"), padx=10).pack(side="left", padx=4)

        self._btn_prev = FlatButton(toolbar, text="< Prev diff",
                                    command=self._prev_diff,
                                    bg="#e67e22", fg="white",
                                    font=("Segoe UI", 9, "bold"), padx=8)
        self._btn_prev.pack(side="left", padx=4)
        self._btn_prev.set_enabled(False)

        self._btn_next = FlatButton(toolbar, text="Next diff >",
                                    command=self._next_diff,
                                    bg="#e67e22", fg="white",
                                    font=("Segoe UI", 9, "bold"), padx=8)
        self._btn_next.pack(side="left", padx=4)
        self._btn_next.set_enabled(False)

        self._lbl_stats = tk.Label(toolbar, text="", bg=pal.get("toolbar_bg", "#2c3e50"),
                                   fg=pal.get("toolbar_fg", "white"),
                                   font=("Segoe UI", 9))
        self._lbl_stats.pack(side="right", padx=12)

        # Paned window with two panels
        paned = tk.PanedWindow(self, orient="horizontal", bg=bg, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=4, pady=4)

        # Left panel
        left_frame = tk.Frame(paned, bg=bg)
        paned.add(left_frame, minsize=300)
        self._lbl_left = tk.Label(left_frame, text=f"Current: {path_left}",
                                  bg=bg, fg=fg, font=("Segoe UI", 9, "bold"), anchor="w")
        self._lbl_left.pack(fill="x", padx=4, pady=2)
        self._tree_left = self._create_tree(left_frame)

        # Right panel
        right_frame = tk.Frame(paned, bg=bg)
        paned.add(right_frame, minsize=300)
        self._lbl_right = tk.Label(right_frame, text="Open a file to compare...",
                                   bg=bg, fg=fg, font=("Segoe UI", 9, "bold"), anchor="w")
        self._lbl_right.pack(fill="x", padx=4, pady=2)
        self._tree_right = self._create_tree(right_frame)

        # Detail panel at bottom
        self._detail_frame = tk.Frame(self, bg=bg)
        self._detail_frame.pack(fill="x", padx=4, pady=4)
        self._detail_label = tk.Label(self._detail_frame, text="",
                                      bg=bg, fg=fg, font=("Consolas", 9),
                                      anchor="w", justify="left")
        self._detail_label.pack(fill="x", padx=4)

        # Populate left
        self._fill_tree(self._tree_left, lines_left)

        # Configure tags — adapt colors based on theme
        is_dark = pal.get("bg", "#f0f2f5").lower() in ("#1e1e2e", "#2b2b3d", "#252536")
        if is_dark:
            tag_added = "#1a3a2a"
            tag_removed = "#3a1a1a"
            tag_modified = "#3a3a1a"
        else:
            tag_added = "#d4edda"
            tag_removed = "#f8d7da"
            tag_modified = "#fff3cd"

        for tree in (self._tree_left, self._tree_right):
            tree.tag_configure("added", background=tag_added)
            tree.tag_configure("removed", background=tag_removed)
            tree.tag_configure("modified", background=tag_modified)

    def _create_tree(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=("num", "type", "content"),
                            show="headings", selectmode="browse")
        tree.heading("num", text="#")
        tree.heading("type", text="Type")
        tree.heading("content", text="Content")
        tree.column("num", width=45, stretch=False)
        tree.column("type", width=65, stretch=False)
        tree.column("content", width=350)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        return tree

    def _fill_tree(self, tree, lines, tags_map=None):
        tree.delete(*tree.get_children())
        for i, line in enumerate(lines):
            rec_type = get_record_type(line)
            content = line[6:60].strip()
            tag = tags_map.get(i, "") if tags_map else ""
            tree.insert("", "end", iid=str(i), values=(i + 1, rec_type, content),
                        tags=(tag,) if tag else ())

    def _open_right_file(self):
        path = filedialog.askopenfilename(
            title="Open ECR file to compare",
            filetypes=[("ECR files", "*.ecr *.ECR"), ("All", "*.*")])
        if not path:
            return

        import os
        self._lines_right = read_ecr_file(path)
        self._lbl_right.config(text=f"Compare: {os.path.basename(path)}")

        # Run comparison
        self._diff_results = compare_files(self._lines_left, self._lines_right)

        # Build tag maps
        left_tags = {}
        right_tags = {}
        diff_count = 0
        for dr in self._diff_results:
            if dr.status == DiffResult.MODIFIED:
                if dr.left_index is not None:
                    left_tags[dr.left_index] = "modified"
                if dr.right_index is not None:
                    right_tags[dr.right_index] = "modified"
                diff_count += 1
            elif dr.status == DiffResult.ADDED:
                if dr.right_index is not None:
                    right_tags[dr.right_index] = "added"
                diff_count += 1
            elif dr.status == DiffResult.REMOVED:
                if dr.left_index is not None:
                    left_tags[dr.left_index] = "removed"
                diff_count += 1

        self._fill_tree(self._tree_left, self._lines_left, left_tags)
        self._fill_tree(self._tree_right, self._lines_right, right_tags)

        self._lbl_stats.config(text=f"{diff_count} difference(s) found")
        self._diff_index = -1

        enabled = diff_count > 0
        self._btn_prev.set_enabled(enabled)
        self._btn_next.set_enabled(enabled)

    def _get_diff_indices(self):
        return [i for i, dr in enumerate(self._diff_results) if dr.status != DiffResult.EQUAL]

    def _navigate_diff(self, direction):
        indices = self._get_diff_indices()
        if not indices:
            return
        if direction > 0:
            self._diff_index = min(self._diff_index + 1, len(indices) - 1)
        else:
            self._diff_index = max(self._diff_index - 1, 0)

        dr = self._diff_results[indices[self._diff_index]]

        # Select in trees
        if dr.left_index is not None:
            iid = str(dr.left_index)
            if self._tree_left.exists(iid):
                self._tree_left.selection_set(iid)
                self._tree_left.see(iid)
        if dr.right_index is not None:
            iid = str(dr.right_index)
            if self._tree_right.exists(iid):
                self._tree_right.selection_set(iid)
                self._tree_right.see(iid)

        # Show field details
        if dr.changed_fields:
            detail = f"Difference {self._diff_index + 1}/{len(indices)}:\n"
            for name, val_a, val_b in dr.changed_fields[:10]:
                detail += f"  {name}: '{val_a}' -> '{val_b}'\n"
            self._detail_label.config(text=detail)
        else:
            self._detail_label.config(
                text=f"Difference {self._diff_index + 1}/{len(indices)}: {dr.status}")

    def _next_diff(self):
        self._navigate_diff(1)

    def _prev_diff(self):
        self._navigate_diff(-1)
