"""Tests for ecrstudio.diff module (non-GUI parts)."""

from ecrstudio.diff import compare_files, DiffResult, _find_changed_fields


class TestCompareFiles:
    """Tests for compare_files function."""

    def test_identical_files(self, minimal_lines):
        results = compare_files(minimal_lines, list(minimal_lines))
        assert all(r.status == DiffResult.EQUAL for r in results)

    def test_added_lines(self):
        lines_a = ["VER   0200000"]
        lines_b = ["VER   0200000", "DOS   TEST    Dossier"]
        results = compare_files(lines_a, lines_b)
        assert results[0].status == DiffResult.EQUAL
        assert results[1].status == DiffResult.ADDED

    def test_removed_lines(self):
        lines_a = ["VER   0200000", "DOS   TEST    Dossier"]
        lines_b = ["VER   0200000"]
        results = compare_files(lines_a, lines_b)
        assert results[0].status == DiffResult.EQUAL
        assert results[1].status == DiffResult.REMOVED

    def test_modified_lines(self):
        lines_a = ["VER   0200000000000000000000          Label A                   0"]
        lines_b = ["VER   0200000000000000000000          Label B                   0"]
        results = compare_files(lines_a, lines_b)
        assert results[0].status == DiffResult.MODIFIED
        assert len(results[0].changed_fields) > 0

    def test_result_count_matches_max_length(self):
        lines_a = ["A", "B", "C"]
        lines_b = ["A", "B", "C", "D", "E"]
        results = compare_files(lines_a, lines_b)
        assert len(results) == 5


class TestFindChangedFields:
    """Tests for _find_changed_fields function."""

    def test_different_types(self):
        changes = _find_changed_fields("VER   something", "DOS   something")
        assert changes[0][0] == "Type"

    def test_same_type_different_fields(self):
        line_a = "VER   0200000000000000000000          Label A                   0"
        line_b = "VER   0200000000000000000000          Label B                   0"
        changes = _find_changed_fields(line_a, line_b)
        assert len(changes) > 0
        field_names = [c[0] for c in changes]
        assert any("libell" in name.lower() or "label" in name.lower()
                    for name in field_names)

    def test_identical_lines_no_changes(self):
        line = "VER   0200000000000000000000          Label test                0"
        changes = _find_changed_fields(line, line)
        assert len(changes) == 0


class TestDiffResult:
    """Tests for DiffResult class."""

    def test_constants(self):
        assert DiffResult.EQUAL == "equal"
        assert DiffResult.MODIFIED == "modified"
        assert DiffResult.ADDED == "added"
        assert DiffResult.REMOVED == "removed"

    def test_attributes(self):
        dr = DiffResult("modified", left_index=0, right_index=0,
                         left_line="A", right_line="B",
                         changed_fields=[("field", "a", "b")])
        assert dr.status == "modified"
        assert dr.left_index == 0
        assert dr.right_index == 0
        assert dr.changed_fields == [("field", "a", "b")]

    def test_default_changed_fields(self):
        dr = DiffResult("equal")
        assert dr.changed_fields == []
