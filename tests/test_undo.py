"""Tests for ecrstudio.undo module."""

from ecrstudio.undo import UndoManager, MAX_HISTORY


class TestUndoManager:
    """Tests for UndoManager class."""

    def test_initial_state(self):
        um = UndoManager()
        assert not um.can_undo
        assert not um.can_redo

    def test_save_and_undo(self):
        um = UndoManager()
        original = ["line1", "line2"]
        um.save_state(original)
        modified = ["line1", "line2", "line3"]
        restored = um.undo(modified)
        assert restored == original

    def test_undo_returns_none_when_empty(self):
        um = UndoManager()
        assert um.undo(["current"]) is None

    def test_redo_after_undo(self):
        um = UndoManager()
        v1 = ["a"]
        um.save_state(v1)
        v2 = ["a", "b"]
        restored = um.undo(v2)
        assert restored == v1
        redone = um.redo(v1)
        assert redone == v2

    def test_redo_returns_none_when_empty(self):
        um = UndoManager()
        assert um.redo(["current"]) is None

    def test_save_clears_redo_stack(self):
        um = UndoManager()
        um.save_state(["v1"])
        um.undo(["v2"])
        assert um.can_redo
        um.save_state(["v3"])
        assert not um.can_redo

    def test_max_history_limit(self):
        um = UndoManager()
        for i in range(MAX_HISTORY + 10):
            um.save_state([f"version_{i}"])
        # Should not exceed MAX_HISTORY
        assert len(um._undo_stack) == MAX_HISTORY

    def test_deep_copy_isolation(self):
        um = UndoManager()
        data = ["mutable"]
        um.save_state(data)
        data.append("changed")
        restored = um.undo(["current"])
        assert restored == ["mutable"]  # original, not mutated

    def test_clear(self):
        um = UndoManager()
        um.save_state(["v1"])
        um.save_state(["v2"])
        um.undo(["v3"])
        um.clear()
        assert not um.can_undo
        assert not um.can_redo

    def test_multiple_undo_redo_cycle(self):
        um = UndoManager()
        um.save_state(["v1"])
        um.save_state(["v2"])
        um.save_state(["v3"])
        current = ["v4"]

        # Undo 3 times
        current = um.undo(current)  # v3
        assert current == ["v3"]
        current = um.undo(current)  # v2
        assert current == ["v2"]
        current = um.undo(current)  # v1
        assert current == ["v1"]

        # Redo 2 times
        current = um.redo(current)  # v2
        assert current == ["v2"]
        current = um.redo(current)  # v3
        assert current == ["v3"]
