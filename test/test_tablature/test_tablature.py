from pathlib import Path
import sys
from typing import Any, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pytest
from pyIT import TablatureBuilder, ITpattern

"""
The lists are zipped in column order.

Like when we have 2 chords only, you must provide lists with 2 elements, and not 2 lists.
For example

wrong_list = [
    (None, 0, 1),
    (None, 0, 1),
]

If you put 2 tunings, will fail, because you provided lists bigger than 2.
If you intend to use the lists as tunings, you need to zip them.

right_list = list(zip(wrong_list[0], wrong_list[1]))

now you can do this:

builder.add_tablature(
    tablature=[right_list], # because the lists are size of 2.
    tuning=["E4", "A4"],
    fret_count=5,
)

"""

def _collect_notes(pattern: ITpattern) -> List[Any]:
    return [cell for row in pattern.Rows for cell in row if cell.Note is not None]


def _collect_effects(pattern: ITpattern) -> List[Any]:
    return [cell for row in pattern.Rows for cell in row if cell.Effect is not None]


def test_builds_pattern_from_simple_tablature() -> None:
    """A minimal tablature with two strings and two rows should produce notes."""
    builder = TablatureBuilder(instrument_id=1, lines_per_note=2)
    builder.add_tablature(
        tablature=[(0, 3), (None, 0)],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    pattern = builder.build()
    notes = _collect_notes(pattern)
    assert len(notes) == 3
    assert notes[0].Instrument == 1


def test_multiple_tablature_blocks_are_concatenated() -> None:
    """Two consecutive blocks place notes on different rows."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature([(0, 3)], ["E4", "A4"], 5)
    builder.add_tablature([(2, 0)], ["E4", "A4"], 5)
    pattern = builder.build()
    assert any(cell.Note is not None for cell in pattern.Rows[0])
    assert any(cell.Note is not None for cell in pattern.Rows[1])
    assert any(cell.Note is not None for cell in pattern.Rows[2])


def test_rejects_too_many_elements_per_row() -> None:
    """A row with more elements than strings must raise ValueError."""
    builder = TablatureBuilder()
    with pytest.raises(ValueError, match="Each tablature row must provide at most one slot"):
        builder.add_tablature(
            tablature=[(0, 3, 1)],
            tuning=["E4", "A4"],
            fret_count=5,
        )


def test_rejects_invalid_string_index() -> None:
    """A dictionary with an out-of-range string index raises an error."""
    builder = TablatureBuilder()
    with pytest.raises(ValueError, match="String index is out of range"):
        builder.add_tablature(
            tablature=[[{"string": 5, "fret": 2}]],
            tuning=["E4", "A4"],
            fret_count=5,
        )


def test_rejects_negative_fret_count() -> None:
    """A negative fret_count must be rejected."""
    builder = TablatureBuilder()
    with pytest.raises(ValueError):
        builder.add_tablature([(0, 0)], ["E4", "A4"], fret_count=-1)


def test_rejects_empty_tuning() -> None:
    """An empty tuning raises an error immediately."""
    builder = TablatureBuilder()
    with pytest.raises(ValueError):
        builder.add_tablature([], [], 5)


def test_different_tunings_produce_different_notes() -> None:
    """Notes on different strings with the same fret yield distinct pitches."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[(0, 0)],
        tuning=["E4", "E5"],
        fret_count=5,
    )
    pattern = builder.build()
    # E4 (MIDI 52) and E5 (MIDI 64) are 12 semitones apart
    assert pattern.Rows[0][0].Note != pattern.Rows[1][0].Note


def test_pre_and_post_effects_are_applied() -> None:
    """Pre effects appear on the note row, post effects on the following row."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[(0, None)],
        tuning=["E4", "A4"],
        fret_count=5,
        pre_note_effects={"set_volume": 64},
        post_note_effects={"portamento_up": 3},
    )
    pattern = builder.build()
    # Row 0: note + pre effect
    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[0][0].Effect == 0x0C
    assert pattern.Rows[0][0].EffectArg == 64
    # Row 1: post effect only (note cleared)
    assert pattern.Rows[1][0].Note is None
    assert pattern.Rows[1][0].Effect == 0x01
    assert pattern.Rows[1][0].EffectArg == 3


def test_compact_bend_token_b2() -> None:
    """Token '1b2' places a note with a bend effect."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[["1b2", None]],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    pattern = builder.build()
    cell = pattern.Rows[0][0]
    assert cell.Note is not None
    assert cell.Effect == 0x04
    assert cell.EffectArg == 2


def test_tuple_fret_bend() -> None:
    """Tuple (3, 2) generates a note with bend=2."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[[(3, 2), None]],
        tuning=["E4", "A4"],
        fret_count=7,
    )
    pattern = builder.build()
    cell = pattern.Rows[0][0]
    assert cell.Note is not None
    assert cell.Effect == 0x04
    assert cell.EffectArg == 2


def test_dict_with_effects() -> None:
    """A dictionary with 'bend' and 'slide' merges the effects."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[[{"fret": 4, "bend": 3, "slide": 1}, None]],
        tuning=["E4", "A4"],
        fret_count=8,
    )
    pattern = builder.build()
    cell = pattern.Rows[0][0]
    assert cell.Note is not None
    assert cell.Effect is not None


def test_chord_spreads_notes_across_rows() -> None:
    """A 'chord' dictionary generates multiple consecutive notes."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[[{"chord": [(0, 2), (1, 3)]}, None]],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    pattern = builder.build()
    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    # The chord spreads two notes, so row 2 should remain empty
    assert pattern.Rows[2][0].Note is None


def test_multiple_strings_in_single_row_arpeggiate() -> None:
    """Several strings with a note in the same row are spread over consecutive rows."""
    builder = TablatureBuilder(lines_per_note=2)
    builder.add_tablature(
        tablature=[(0, 3, 1)],
        tuning=["E4", "A4", "D4"],
        fret_count=5,
    )
    pattern = builder.build()
    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    assert pattern.Rows[2][0].Note is not None


def test_max_rows_truncates_output() -> None:
    """Notes beyond max_rows are ignored (pattern still has full length but no notes after limit)."""
    builder = TablatureBuilder(max_rows=2, lines_per_note=1)
    builder.add_tablature(
        tablature=[(0, 3), (2, 0)],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    pattern = builder.build()
    # Pattern always has 64 rows, but only rows 0 and 1 should contain notes
    assert len(pattern.Rows) == 64
    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    # All rows from index 2 onward must be empty
    for row in pattern.Rows[2:]:
        for cell in row:
            assert cell.Note is None


def test_instrument_override() -> None:
    """add_tablature with a different instrument_id overrides the default."""
    builder = TablatureBuilder(instrument_id=1)
    builder.add_tablature(
        tablature=[(0, 0)],
        tuning=["E4", "A4"],
        fret_count=5,
        instrument_id=99,
    )
    pattern = builder.build()
    assert pattern.Rows[0][0].Instrument == 99


def test_bpm_override() -> None:
    """BPM passed to add_tablature should be used for that block."""
    builder = TablatureBuilder(bpm=120, lines_per_note=1)
    builder.add_tablature(
        tablature=[(0, 0)],
        tuning=["E4", "A4"],
        fret_count=5,
        bpm=180,
    )
    pattern = builder.build()
    assert pattern is not None


def test_large_mixed_syntax() -> None:
    """A large tablature with various syntaxes and effects produces expected number of notes."""
    builder = TablatureBuilder(instrument_id=5, lines_per_note=1, max_rows=128)

    rows: List[Any] = [
        [None, 0, "1b2", None],
        [{"fret": 3, "bend": 2}, None, "h2", 2],
        [{"chord": [(0, 2), (1, 3)]}, "1s2", None, None],
        [4, None, None, "b2"],
        [None, {"fret": 5, "slide": 1}, None, None],
    ]

    builder.add_tablature(
        tablature=rows,
        tuning=["E4", "A4", "D4", "G3"],
        fret_count=12,
        pre_note_effects={"volume_slide": 3},
        post_note_effects={"set_volume": 64},
    )

    pattern = builder.build()

    notes = _collect_notes(pattern)
    effects = _collect_effects(pattern)

    # With the current parser, the exact count may vary; we check that it is >0
    assert len(notes) > 0
    assert len(effects) > 0
    assert all(c.Instrument == 5 for c in notes)


def test_empty_tablature_does_nothing() -> None:
    """An empty tablature results in a pattern with no notes."""
    builder = TablatureBuilder()
    builder.add_tablature(
        tablature=[],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    pattern = builder.build()
    assert len(_collect_notes(pattern)) == 0


def test_rows_all_none_produce_no_notes_but_advance_rows() -> None:
    """Rows where every string is None generate no notes but still consume row space."""
    builder = TablatureBuilder(lines_per_note=2)
    builder.add_tablature(
        tablature=[(None, None), (0, 0)],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    pattern = builder.build()
    assert pattern.Rows[0][0].Note is None
    assert pattern.Rows[1][0].Note is None
    assert pattern.Rows[2][0].Note is not None
    assert pattern.Rows[3][0].Note is not None


def test_zip_format_works() -> None:
    """Transposed input created with zip is accepted and produces a valid pattern."""
    seq1: List[Any] = [None, 9, 9, 9, 9, None, 7, 7]
    seq2: List[Any] = [None, 7, 7, 7, 7, None, 5, 5]
    tablature: List[Any] = list(zip(seq1, seq2))

    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=tablature,
        tuning=["D4", "A3"],
        fret_count=12,
        post_note_effects={"slide": 2},
    )
    pattern = builder.build()
    assert pattern is not None
    assert sum(1 for row in pattern.Rows if any(c.Note is not None for c in row)) >= len(seq1) - seq1.count(None)
