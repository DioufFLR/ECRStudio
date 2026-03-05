"""Tests for ecrstudio.export module."""

import os
import csv
from ecrstudio.export import export_to_csv


class TestExportCsv:
    """Tests for export_to_csv function."""

    def test_export_creates_file(self, minimal_lines, tmp_path):
        output = str(tmp_path / "test.csv")
        export_to_csv(minimal_lines, output)
        assert os.path.exists(output)

    def test_export_semicolon_separator(self, minimal_lines, tmp_path):
        output = str(tmp_path / "test.csv")
        export_to_csv(minimal_lines, output, separator=";")
        with open(output, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        assert ";" in content

    def test_export_utf8_bom(self, minimal_lines, tmp_path):
        output = str(tmp_path / "test.csv")
        export_to_csv(minimal_lines, output)
        with open(output, 'rb') as f:
            bom = f.read(3)
        assert bom == b'\xef\xbb\xbf'  # UTF-8 BOM

    def test_export_filter_by_type(self, minimal_lines, tmp_path):
        output = str(tmp_path / "test.csv")
        export_to_csv(minimal_lines, output, record_types=["MVT"])
        with open(output, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        assert "MVT" in content
        assert "--- VER ---" not in content

    def test_export_contains_headers(self, minimal_lines, tmp_path):
        output = str(tmp_path / "test.csv")
        export_to_csv(minimal_lines, output)
        with open(output, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        assert "Line #" in content

    def test_export_custom_separator(self, minimal_lines, tmp_path):
        output = str(tmp_path / "test.csv")
        export_to_csv(minimal_lines, output, separator=",")
        with open(output, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=",")
            rows = list(reader)
        assert len(rows) > 0
