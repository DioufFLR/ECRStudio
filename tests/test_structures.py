"""Tests for ecrstudio.structures module."""

from ecrstudio.structures import STRUCTURES


class TestStructures:
    """Tests for the STRUCTURES dictionary."""

    EXPECTED_TYPES = ["VER", "DOS", "EXO", "CPT", "ECR", "MVT",
                      "TVA", "JOU", "TIERS", "ECHMVT", "ANAMVT"]

    def test_all_types_present(self):
        for rec_type in self.EXPECTED_TYPES:
            assert rec_type in STRUCTURES, f"Missing structure for {rec_type}"

    def test_no_extra_types(self):
        for key in STRUCTURES:
            assert key in self.EXPECTED_TYPES, f"Unexpected structure: {key}"

    def test_field_tuples_have_four_elements(self):
        for rec_type, struct in STRUCTURES.items():
            for pos, field in struct.items():
                assert len(field) == 4, (
                    f"{rec_type} pos {pos}: expected 4-tuple, got {len(field)}"
                )
                name, length, ftype, required = field
                assert isinstance(name, str)
                assert isinstance(length, int)
                assert ftype in ("Alpha", "Num", "Date"), (
                    f"{rec_type}.{name}: unknown type '{ftype}'"
                )
                assert isinstance(required, bool)

    def test_positions_are_positive_integers(self):
        for rec_type, struct in STRUCTURES.items():
            for pos in struct.keys():
                assert isinstance(pos, int) and pos >= 1, (
                    f"{rec_type}: invalid position {pos}"
                )

    def test_first_field_is_record_type(self):
        for rec_type, struct in STRUCTURES.items():
            assert 1 in struct, f"{rec_type}: missing position 1"
            name, length, _, required = struct[1]
            assert "type" in name.lower() or "enregistrement" in name.lower(), (
                f"{rec_type}: first field should be record type, got '{name}'"
            )
            assert required is True

    def test_no_overlapping_fields(self):
        for rec_type, struct in STRUCTURES.items():
            ranges = []
            for pos, (name, length, _, _) in sorted(struct.items()):
                start = pos
                end = pos + length - 1
                for prev_start, prev_end, prev_name in ranges:
                    assert start > prev_end, (
                        f"{rec_type}: field '{name}' at {start}-{end} "
                        f"overlaps with '{prev_name}' at {prev_start}-{prev_end}"
                    )
                ranges.append((start, end, name))

    def test_required_fields_exist_per_type(self):
        """Each type should have at least one required field (the record type)."""
        for rec_type, struct in STRUCTURES.items():
            required_count = sum(1 for _, (_, _, _, req) in struct.items() if req)
            assert required_count >= 1, f"{rec_type}: no required fields"
