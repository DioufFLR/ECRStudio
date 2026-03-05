"""
ECR file validation engine.

Checks hierarchy, required fields, date formats, and debit/credit balance.
Returns a list of ValidationError objects with severity, message, and line index.
"""

import re
from .structures import STRUCTURES
from .parser import read_field, get_record_type
from .constants import HIERARCHY

DATE_PATTERN = re.compile(r"^\d{8}$")
VALID_DATE_EMPTY = re.compile(r"^[\s0]*$")


class ValidationError:
    """Represents a validation issue."""

    ERROR = "error"
    WARNING = "warning"

    def __init__(self, severity, message, line_index=None, field_name=None):
        self.severity = severity
        self.message = message
        self.line_index = line_index
        self.field_name = field_name

    def __repr__(self):
        prefix = "ERR" if self.severity == self.ERROR else "WARN"
        line_info = f" (line {self.line_index + 1})" if self.line_index is not None else ""
        return f"[{prefix}]{line_info} {self.message}"


def validate_file(lines):
    """Run all validations on a list of ECR lines. Returns list of ValidationError."""
    errors = []
    errors.extend(_validate_hierarchy(lines))
    errors.extend(_validate_required_fields(lines))
    errors.extend(_validate_dates(lines))
    errors.extend(_validate_balance(lines))
    errors.extend(_validate_line_lengths(lines))
    return errors


def _validate_hierarchy(lines):
    """Check that the file follows the VER > DOS > EXO > ... hierarchy."""
    errors = []
    if not lines:
        errors.append(ValidationError(ValidationError.ERROR, "Empty file"))
        return errors

    first_type = get_record_type(lines[0])
    if first_type != "VER":
        errors.append(ValidationError(
            ValidationError.ERROR,
            f"First line must be VER, found '{first_type}'",
            line_index=0
        ))

    # Track hierarchy stack
    parent_stack = []  # Stack of (type, line_index)

    for i, line in enumerate(lines):
        rec_type = get_record_type(line)
        if rec_type not in HIERARCHY and rec_type not in STRUCTURES:
            errors.append(ValidationError(
                ValidationError.WARNING,
                f"Unknown record type '{rec_type}'",
                line_index=i
            ))
            continue

        if rec_type == "VER":
            parent_stack = [("VER", i)]
            continue

        # Find valid parent
        valid = False
        for parent_type, _children in HIERARCHY.items():
            if rec_type in HIERARCHY.get(parent_type, []):
                # Check if this parent type exists in the stack
                for j in range(len(parent_stack) - 1, -1, -1):
                    if parent_stack[j][0] == parent_type:
                        parent_stack = parent_stack[:j + 1]
                        parent_stack.append((rec_type, i))
                        valid = True
                        break
            if valid:
                break

        if not valid and i > 0:
            errors.append(ValidationError(
                ValidationError.WARNING,
                f"'{rec_type}' has no valid parent in hierarchy",
                line_index=i
            ))

    return errors


def _validate_required_fields(lines):
    """Check that required fields are not empty."""
    errors = []
    for i, line in enumerate(lines):
        rec_type = get_record_type(line)
        struct = STRUCTURES.get(rec_type)
        if not struct:
            continue

        for position, (name, length, _field_type, required) in sorted(struct.items()):
            if not required:
                continue
            if name == "Type enregistrement":
                continue
            value = read_field(line, position, length).strip()
            if not value or value == '0' * length:
                errors.append(ValidationError(
                    ValidationError.WARNING,
                    f"Required field '{name}' is empty",
                    line_index=i,
                    field_name=name
                ))

    return errors


def _validate_dates(lines):
    """Check that Date fields contain valid dates (jjmmaaaa)."""
    errors = []
    for i, line in enumerate(lines):
        rec_type = get_record_type(line)
        struct = STRUCTURES.get(rec_type)
        if not struct:
            continue

        for position, (name, length, field_type, _required) in sorted(struct.items()):
            if field_type != "Date":
                continue
            value = read_field(line, position, length)
            if VALID_DATE_EMPTY.match(value):
                continue
            if not DATE_PATTERN.match(value.strip()):
                errors.append(ValidationError(
                    ValidationError.ERROR,
                    f"Invalid date format in '{name}': '{value.strip()}' (expected jjmmaaaa)",
                    line_index=i,
                    field_name=name
                ))
                continue
            # Basic date range check
            day = int(value[:2])
            month = int(value[2:4])
            if month < 1 or month > 12 or day < 1 or day > 31:
                errors.append(ValidationError(
                    ValidationError.ERROR,
                    f"Invalid date value in '{name}': day={day}, month={month}",
                    line_index=i,
                    field_name=name
                ))

    return errors


def _validate_balance(lines):
    """Check that debit/credit are balanced within each ECR group."""
    errors = []
    current_ecr_index = None
    total_debit = 0.0
    total_credit = 0.0

    def _check_balance():
        if current_ecr_index is not None and (total_debit > 0 or total_credit > 0):
            diff = abs(total_debit - total_credit)
            if diff > 0.01:  # Tolerance for floating point
                errors.append(ValidationError(
                    ValidationError.ERROR,
                    f"Unbalanced entry: debit={total_debit:.2f}, credit={total_credit:.2f}, diff={diff:.2f}",
                    line_index=current_ecr_index
                ))

    for i, line in enumerate(lines):
        rec_type = get_record_type(line)
        if rec_type == "ECR":
            _check_balance()
            current_ecr_index = i
            total_debit = 0.0
            total_credit = 0.0
        elif rec_type == "MVT" and current_ecr_index is not None:
            debit_str = read_field(line, 47, 13).strip()
            credit_str = read_field(line, 60, 13).strip()
            try:
                total_debit += float(debit_str) if debit_str else 0.0
            except ValueError:
                pass
            try:
                total_credit += float(credit_str) if credit_str else 0.0
            except ValueError:
                pass

    _check_balance()
    return errors


def _validate_line_lengths(lines):
    """Warn about lines that are shorter than expected for their type."""
    errors = []
    for i, line in enumerate(lines):
        rec_type = get_record_type(line)
        struct = STRUCTURES.get(rec_type)
        if not struct:
            continue
        max_pos = max(pos + length for pos, (_name, length, _t, _r) in struct.items())
        if len(line) < max_pos - 1:
            errors.append(ValidationError(
                ValidationError.WARNING,
                f"Line is shorter than expected ({len(line)} < {max_pos - 1} chars)",
                line_index=i
            ))
    return errors
