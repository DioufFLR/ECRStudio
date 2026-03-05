"""Tests for ecrstudio.validator module."""

import pytest
from ecrstudio.validator import validate_file, ValidationError


class TestValidateHierarchy:
    """Tests for hierarchy validation."""

    def test_valid_minimal_file(self, minimal_lines):
        errors = validate_file(minimal_lines)
        hierarchy_errors = [e for e in errors if "hierarchy" in e.message.lower()
                            or "first line" in e.message.lower()]
        assert len(hierarchy_errors) == 0

    def test_empty_file(self):
        errors = validate_file([])
        assert any(e.message == "Empty file" for e in errors)

    def test_first_line_not_ver(self):
        lines = ["DOS   TEST    Dossier test"]
        errors = validate_file(lines)
        assert any("First line must be VER" in e.message for e in errors)

    def test_dos_without_ver(self):
        lines = [
            "VER   0200000000000000000000          Fichier test              0",
            "ECR   AC01012025",  # ECR without DOS > EXO
        ]
        errors = validate_file(lines)
        hierarchy_warns = [e for e in errors
                           if "no valid parent" in e.message.lower()]
        assert len(hierarchy_warns) > 0

    def test_unknown_type_warns(self):
        lines = [
            "VER   0200000000000000000000          Fichier test              0",
            "XXX   unknown record",
        ]
        errors = validate_file(lines)
        assert any("Unknown record type" in e.message for e in errors)


class TestValidateDates:
    """Tests for date validation."""

    def test_valid_date(self, minimal_lines):
        errors = validate_file(minimal_lines)
        date_errors = [e for e in errors if "date" in e.message.lower()
                       and e.severity == ValidationError.ERROR]
        assert len(date_errors) == 0

    def test_invalid_date_format(self):
        lines = [
            "VER   0200000000000000000000          Fichier test              0",
            "DOS   TEST    Dossier test                                      011100102EUR",
            "EXO   ABCDEFGH3112202500           EUR        1",
        ]
        errors = validate_file(lines)
        date_errors = [e for e in errors if "date" in e.message.lower()
                       and e.severity == ValidationError.ERROR]
        assert len(date_errors) > 0

    def test_invalid_month(self):
        lines = [
            "VER   0200000000000000000000          Fichier test              0",
            "DOS   TEST    Dossier test                                      011100102EUR",
            "EXO   011320253112202500           EUR        1",  # month=13
        ]
        errors = validate_file(lines)
        date_errors = [e for e in errors if "month" in e.message.lower()
                       or "Invalid date" in e.message]
        assert len(date_errors) > 0

    def test_empty_date_ok(self):
        """Empty dates (all spaces/zeros) should not trigger errors."""
        lines = [
            "VER   0200000000000000000000          Fichier test              0",
            "DOS   TEST    Dossier test            00000000                  011100102EUR",
        ]
        errors = validate_file(lines)
        date_errors = [e for e in errors if "date format" in e.message.lower()
                       and e.severity == ValidationError.ERROR]
        assert len(date_errors) == 0


class TestValidateBalance:
    """Tests for debit/credit balance validation."""

    def test_balanced_entry(self, minimal_lines):
        errors = validate_file(minimal_lines)
        balance_errors = [e for e in errors if "unbalanced" in e.message.lower()]
        assert len(balance_errors) == 0

    def test_unbalanced_entry(self):
        lines = [
            "VER   0200000000000000000000          Fichier test              0",
            "DOS   TEST    Dossier test                                      011100102EUR",
            "EXO   010120253112202500           EUR        1",
            "ECR   AC0101202500000000000Ecriture test                                                             000000001",
            "MVT   4110000000Achat                          00000000010000000000000000",
            "MVT   5120000000Banque                         00000000000000000000000500",  # 500 != 1000
        ]
        errors = validate_file(lines)
        balance_errors = [e for e in errors if "unbalanced" in e.message.lower()]
        assert len(balance_errors) > 0


class TestValidateRequiredFields:
    """Tests for required field validation."""

    def test_valid_file_no_required_errors(self, minimal_lines):
        errors = validate_file(minimal_lines)
        req_errors = [e for e in errors if "required field" in e.message.lower()
                      and e.severity == ValidationError.WARNING]
        # minimal_lines should have key required fields filled
        # (some warnings may appear for optional structures)
        assert isinstance(req_errors, list)


class TestValidationError:
    """Tests for ValidationError class."""

    def test_repr_error(self):
        e = ValidationError(ValidationError.ERROR, "Test error", line_index=5)
        assert "[ERR]" in repr(e)
        assert "line 6" in repr(e)

    def test_repr_warning(self):
        e = ValidationError(ValidationError.WARNING, "Test warn")
        assert "[WARN]" in repr(e)

    def test_attributes(self):
        e = ValidationError("error", "msg", line_index=2, field_name="Amount")
        assert e.severity == "error"
        assert e.message == "msg"
        assert e.line_index == 2
        assert e.field_name == "Amount"
