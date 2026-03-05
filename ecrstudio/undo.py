"""
Undo/Redo manager for ECRStudio.

Stores snapshots of the lines list to support multi-level undo/redo.
"""

import copy

MAX_HISTORY = 50


class UndoManager:
    """Manages undo/redo history for a list of lines."""

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def save_state(self, lines):
        """Save a snapshot of the current lines before a modification."""
        self._undo_stack.append(copy.deepcopy(lines))
        if len(self._undo_stack) > MAX_HISTORY:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, current_lines):
        """Undo the last change. Returns the restored lines or None if nothing to undo."""
        if not self._undo_stack:
            return None
        self._redo_stack.append(copy.deepcopy(current_lines))
        return self._undo_stack.pop()

    def redo(self, current_lines):
        """Redo the last undone change. Returns the restored lines or None if nothing to redo."""
        if not self._redo_stack:
            return None
        self._undo_stack.append(copy.deepcopy(current_lines))
        return self._redo_stack.pop()

    @property
    def can_undo(self):
        return len(self._undo_stack) > 0

    @property
    def can_redo(self):
        return len(self._redo_stack) > 0

    def clear(self):
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
