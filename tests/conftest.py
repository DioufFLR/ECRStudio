"""Shared fixtures for ECRStudio tests."""

import pytest

# Minimal valid ECR file lines (VER + DOS + EXO + ECR + 2 balanced MVT)
MINIMAL_LINES = [
    "VER   0200000000000000000000          Fichier test              0",
    "DOS   TEST    Dossier test                                      011100102EUR",
    "EXO   010120253112202500           EUR        1",
    "ECR   AC0101202500000000000Ecriture test                                                             000000001",
    "MVT   4110000000Achat test                    00000000010000000000000000",
    "MVT   5120000000Banque test                   00000000000000000000001000",
]


@pytest.fixture
def minimal_lines():
    """Return a minimal valid set of ECR lines."""
    return list(MINIMAL_LINES)


@pytest.fixture
def example_ecr_path():
    """Return the path to the example ECR file."""
    import os
    return os.path.join(os.path.dirname(__file__), "..", "examples", "exemple.ECR")


@pytest.fixture
def tmp_ecr_path(tmp_path):
    """Return a temp path for writing ECR files."""
    return str(tmp_path / "test_output.ECR")
