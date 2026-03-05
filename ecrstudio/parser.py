"""
ECR file parser and field manipulation utilities.

Handles reading/writing ECR files in ANSI (latin-1) encoding with \\r\\n line endings,
and extracting/writing positional fields according to ISAgri specifications.
"""


def read_field(line, position, length):
    """Extract a field value from a line at the given 1-based position."""
    start = position - 1
    end = start + length
    if end > len(line):
        return line[start:].ljust(length)
    return line[start:end]


def write_field(line, position, length, value, field_type="Alpha"):
    """Write a formatted field value into a line at the given 1-based position.

    Alpha/Date fields are left-aligned and space-padded.
    Num fields are right-aligned and zero-padded.
    """
    start = position - 1
    end = start + length
    value = str(value)
    if field_type == "Num":
        formatted = value.strip().rjust(length, '0')
    else:
        formatted = value.ljust(length)
    formatted = formatted[:length]
    padded_line = line.ljust(end)
    return padded_line[:start] + formatted + padded_line[end:]


def get_record_type(line):
    """Return the record type code (first 6 chars, stripped)."""
    return line[:6].strip()


def read_ecr_file(path):
    """Read an ECR file and return a list of lines (without line endings)."""
    with open(path, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    return [line.rstrip('\r\n') for line in lines]


def save_ecr_file(path, lines):
    """Save lines to an ECR file with ANSI encoding and \\r\\n line endings."""
    with open(path, 'w', encoding='latin-1', newline='') as f:
        for line in lines:
            f.write(line.rstrip('\r\n') + '\r\n')
