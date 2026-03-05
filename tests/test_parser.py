"""Tests for ecrstudio.parser module."""

import os
import pytest
from ecrstudio.parser import read_field, write_field, get_record_type, read_ecr_file, save_ecr_file


class TestReadField:
    """Tests for read_field (1-based position extraction)."""

    def test_basic_extraction(self):
        line = "VER   0200000"
        assert read_field(line, 1, 6) == "VER   "

    def test_position_is_one_based(self):
        line = "ABCDEFGHIJ"
        assert read_field(line, 1, 3) == "ABC"
        assert read_field(line, 4, 3) == "DEF"

    def test_pads_when_line_too_short(self):
        line = "VER"
        result = read_field(line, 1, 6)
        assert len(result) == 6
        assert result == "VER   "

    def test_exact_length(self):
        line = "ABCDEF"
        assert read_field(line, 1, 6) == "ABCDEF"

    def test_middle_of_line(self):
        line = "VER   0200000"
        assert read_field(line, 7, 7) == "0200000"


class TestWriteField:
    """Tests for write_field (positional field writing)."""

    def test_alpha_field_left_aligned_space_padded(self):
        line = "      " * 10
        result = write_field(line, 1, 6, "VER", "Alpha")
        assert result[:6] == "VER   "

    def test_num_field_right_aligned_zero_padded(self):
        line = "      " * 10
        result = write_field(line, 7, 7, "200", "Num")
        assert result[6:13] == "0000200"

    def test_truncates_to_field_length(self):
        line = "          "
        result = write_field(line, 1, 3, "ABCDEF", "Alpha")
        assert result[:3] == "ABC"

    def test_preserves_other_fields(self):
        line = "VER   0200000rest_of_line"
        result = write_field(line, 7, 7, "300", "Num")
        assert result[:6] == "VER   "
        assert result[6:13] == "0000300"
        assert result[13:] == "rest_of_line"

    def test_extends_line_if_needed(self):
        line = "VER"
        result = write_field(line, 7, 7, "200", "Num")
        assert len(result) >= 13
        assert result[6:13] == "0000200"

    def test_date_field_left_aligned(self):
        line = "          "
        result = write_field(line, 1, 8, "01012025", "Date")
        assert result[:8] == "01012025"


class TestGetRecordType:
    """Tests for get_record_type."""

    def test_ver(self):
        assert get_record_type("VER   0200000") == "VER"

    def test_dos(self):
        assert get_record_type("DOS   ORA     Test") == "DOS"

    def test_mvt(self):
        assert get_record_type("MVT   4110000000Achat") == "MVT"

    def test_echmvt(self):
        assert get_record_type("ECHMVT0000001000030012025") == "ECHMVT"

    def test_strips_whitespace(self):
        assert get_record_type("ECR   AC01012025") == "ECR"

    def test_short_line(self):
        assert get_record_type("VER") == "VER"


class TestReadEcrFile:
    """Tests for read_ecr_file."""

    def test_reads_example_file(self, example_ecr_path):
        if not os.path.exists(example_ecr_path):
            pytest.skip("Example ECR file not found")
        lines = read_ecr_file(example_ecr_path)
        assert len(lines) > 0
        assert get_record_type(lines[0]) == "VER"

    def test_strips_line_endings(self, example_ecr_path):
        if not os.path.exists(example_ecr_path):
            pytest.skip("Example ECR file not found")
        lines = read_ecr_file(example_ecr_path)
        for line in lines:
            assert not line.endswith('\r')
            assert not line.endswith('\n')


class TestSaveEcrFile:
    """Tests for save_ecr_file."""

    def test_roundtrip(self, example_ecr_path, tmp_ecr_path):
        if not os.path.exists(example_ecr_path):
            pytest.skip("Example ECR file not found")
        lines = read_ecr_file(example_ecr_path)
        save_ecr_file(tmp_ecr_path, lines)
        reloaded = read_ecr_file(tmp_ecr_path)
        assert lines == reloaded

    def test_writes_crlf_endings(self, tmp_ecr_path, minimal_lines):
        save_ecr_file(tmp_ecr_path, minimal_lines)
        with open(tmp_ecr_path, 'rb') as f:
            raw = f.read()
        assert b'\r\n' in raw
        # No bare \n (every \n should be preceded by \r)
        lines_raw = raw.split(b'\r\n')
        for part in lines_raw[:-1]:  # last may be empty
            assert b'\n' not in part

    def test_writes_latin1_encoding(self, tmp_ecr_path, minimal_lines):
        save_ecr_file(tmp_ecr_path, minimal_lines)
        with open(tmp_ecr_path, 'r', encoding='latin-1') as f:
            content = f.read()
        assert "VER" in content

    def test_saves_minimal_file(self, tmp_ecr_path, minimal_lines):
        save_ecr_file(tmp_ecr_path, minimal_lines)
        reloaded = read_ecr_file(tmp_ecr_path)
        assert len(reloaded) == len(minimal_lines)
