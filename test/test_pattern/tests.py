from pathlib import Path
import sys
from typing import Any, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pyIT.pyIT import PatternBuilder


def test_note_name_to_number_supports_common_note_names() -> None:
    """Convert standard note names and sharps into IT-compatible note numbers."""
    builder = PatternBuilder()

    assert builder.note_name_to_number("C4") == 48
    assert builder.note_name_to_number("F#5") == 66
    assert builder.note_name_to_number("A-4") == 57
    assert builder.note_name_to_number("D-4") == 50


def test_note_name_to_number_supports_portuguese_aliases() -> None:
    """Accept the Portuguese note aliases used by the project examples."""
    builder = PatternBuilder()

    assert builder.note_name_to_number("DO") == 60
    assert builder.note_name_to_number("RE") == 62
    assert builder.note_name_to_number("MI") == 64


def test_note_name_to_number_falls_back_to_middle_c_for_invalid_names() -> None:
    """Keep the builder robust when an invalid note name is supplied."""
    builder = PatternBuilder()

    assert builder.note_name_to_number("invalid") == 60
    assert builder.note_name_to_number(None) is None


def test_build_pattern_places_notes_on_expected_rows_and_keeps_instrument() -> None:
    """Place notes on the expected rows according to the configured spacing and assign the instrument."""
    builder = PatternBuilder(bpm=240, lines_per_note=2)
    sequence: List[Any] = ["D-4", "D-4", "D-5", None, None, "A-4", None, None]

    pattern = builder.build_pattern(sequence, instrument_id=7)

    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[0][0].Instrument == 7
    assert pattern.Rows[0][0].Volume == 64
    assert pattern.Rows[2][0].Note == builder.note_name_to_number("D-4")
    assert pattern.Rows[4][0].Note == builder.note_name_to_number("D-5")
    assert pattern.Rows[6][0].Note is None


def test_build_pattern_respects_lines_per_note_spacing() -> None:
    """Ensure that each note consumes the configured number of rows."""
    builder = PatternBuilder(lines_per_note=3)
    pattern = builder.build_pattern(["C4", "E4", "G4"], instrument_id=2)

    assert pattern.Rows[0][0].Note == builder.note_name_to_number("C4")
    assert pattern.Rows[3][0].Note == builder.note_name_to_number("E4")
    assert pattern.Rows[6][0].Note == builder.note_name_to_number("G4")
    assert pattern.Rows[1][0].Note is None


def test_build_pattern_skips_none_entries_and_keeps_the_pattern_dense() -> None:
    """Treat None values as rests and avoid writing notes into those rows."""
    builder = PatternBuilder(lines_per_note=1)
    pattern = builder.build_pattern([None, "C4", None, "D4", None], instrument_id=3)

    assert pattern.Rows[0][0].Note is None
    assert pattern.Rows[1][0].Note == builder.note_name_to_number("C4")
    assert pattern.Rows[3][0].Note == builder.note_name_to_number("D4")
    assert pattern.Rows[4][0].Note is None


def test_build_pattern_truncates_sequences_beyond_the_pattern_limit() -> None:
    """Stop placing notes once the 64-row pattern limit has been reached."""
    builder = PatternBuilder(lines_per_note=1)
    long_sequence = ["C4"] * 80

    pattern = builder.build_pattern(long_sequence, instrument_id=1)

    populated_rows = [row_index for row_index in range(64) if pattern.Rows[row_index][0].Note is not None]

    assert len(populated_rows) == 64
    assert pattern.Rows[63][0].Note == builder.note_name_to_number("C4")


def test_build_pattern_matches_the_reference_sequence_shape() -> None:
    """Mirror the sequence used by the reference script and verify the row layout."""
    builder = PatternBuilder(bpm=240, lines_per_note=2)
    sequence: List[Any] = [
        "D-4", "D-4", "D-5", None, None, "A-4", None, None,
        "G#4", None, None, "G-4", None, "F-4", "D-4", "F-4",
        "G-4", "C-4", "C-4", "D-5", None, None, "A-4", None,
        "G#4", None, None, "G-4", None, None, None,
    ]

    pattern = builder.build_pattern(sequence, instrument_id=1)

    expected_rows = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
    populated_rows = [row_index for row_index in expected_rows if pattern.Rows[row_index][0].Note is not None]

    assert populated_rows == [0, 2, 4, 10, 16, 22, 26, 28, 30]
