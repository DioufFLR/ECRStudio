"""
Export ECR data to CSV format.
"""

import csv
from .structures import STRUCTURES
from .parser import read_field, get_record_type


def export_to_csv(lines, output_path, separator=";", record_types=None):
    """Export ECR lines to a CSV file.

    Args:
        lines: List of ECR line strings.
        output_path: Path to write the CSV file.
        separator: CSV delimiter (default ';' for Excel FR).
        record_types: Optional list of types to include. None = all.
    """
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=separator)

        # Group lines by type
        lines_by_type = {}
        for i, line in enumerate(lines):
            rec_type = get_record_type(line)
            if record_types and rec_type not in record_types:
                continue
            if rec_type not in lines_by_type:
                lines_by_type[rec_type] = []
            lines_by_type[rec_type].append((i, line))

        for rec_type, typed_lines in lines_by_type.items():
            struct = STRUCTURES.get(rec_type)
            if not struct:
                continue

            # Write section header
            writer.writerow([f"--- {rec_type} ---"])

            # Write column headers
            headers = ["Line #"]
            for _pos, (name, _length, _ftype, _req) in sorted(struct.items()):
                headers.append(name)
            writer.writerow(headers)

            # Write data rows
            for line_idx, line in typed_lines:
                row = [str(line_idx + 1)]
                for pos, (_name, length, _ftype, _req) in sorted(struct.items()):
                    value = read_field(line, pos, length).strip()
                    row.append(value)
                writer.writerow(row)

            writer.writerow([])  # Blank line between sections
