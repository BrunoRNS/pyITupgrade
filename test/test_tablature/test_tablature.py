from pathlib import Path
import sys
from typing import Any, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pytest

from pyIT import TablatureBuilder


def test_builds_pattern_from_tablature_and_combines_multiple_inputs() -> None:
    """Build a simple pattern from two tablature blocks and verify that both notes land in the pattern."""
    builder = TablatureBuilder(instrument_id=1, lines_per_note=2)

    builder.add_tablature(
        tablature=[
            (0, 3),
            (None, 0)
        ],
        tuning=["E4", "A4"],
        fret_count=5,
    )
    builder.add_tablature(
        tablature=[
            (1, 0),
            (2, 2)
        ],
        tuning=["E4", "A4"],
        fret_count=5,
        pre_note_effects={"volume_slide": 4},
    )

    pattern = builder.build()

    assert pattern is not None
    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[2][0].Note is not None


def test_rejects_invalid_tablature_shape() -> None:
    """Reject rows that declare more values than the tuning contains."""
    builder = TablatureBuilder()
    with pytest.raises(ValueError):
        builder.add_tablature(
            tablature=[
                (0,    3,   1   ),
                (None, 1,   None)
            ],
            tuning=["E4"],
            fret_count=5,
        )


def test_uses_each_string_tuning_when_converting_frets() -> None:
    """Verify that note conversion uses the tuning of each string rather than a single global pitch."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[
            (0, 3),
            (0, None)
        ],
        tuning=["E4", "A4"],
        fret_count=5,
    )

    pattern = builder.build()

    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    assert pattern.Rows[0][0].Note != pattern.Rows[1][0].Note


def test_supports_chords_and_guitar_style_effects() -> None:
    """Allow chord-like structures and bend effects to coexist in the same row."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        tablature=[
            [
                (0, 2),
                {"fret": 3, "bend": 2}
            ]
        ],
        tuning=["E4", "A4"],
        fret_count=7,
    )

    pattern = builder.build()

    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    assert pattern.Rows[2][0].Effect is not None
    assert pattern.Rows[2][0].EffectArg is not None


def test_various_tuning() -> None:
    """Verify that notes from several blocks are placed across rows and keep their instrument assignments."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        [
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (1,    2,    3,    4,    None, None),
        ],
        ["E5", "B5", "G4", "D4", "A3", "E3"],
        22,
    )

    builder.add_tablature(
        [
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (1,    2,    3,    4,    None, None),
            (None, None, None, None, None, None),
        ],
        ["E5", "B5", "G4", "D4", "A3", "E3"],
        22,
    )

    builder.add_tablature(
        [
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (1,    2,    3,    4,    None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
        ],
        ["E5", "B5", "G4", "D4", "A3", "E3"],
        22,
    )

    builder.add_tablature(
        [
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (1,    2,    3,    4,    None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
        ],
        ["E5", "B5", "G4", "D4", "A3", "E3"],
        22,
    )

    builder.add_tablature(
        [
            (None, None, None, None, None, None),
            (1,    2,    3,    4,    None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
        ],
        ["E5", "B5", "G4", "D4", "A3", "E3"],
        22,
    )

    builder.add_tablature(
        [
            (1,    2,    3,    4,    None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
        ],
        ["E5", "B5", "G4", "D4", "A3", "E3"],
        22,
    )

    pattern = builder.build()

    for row_index in (5, 6, 7, 8):
        assert pattern.Rows[row_index][0].Note is not None
        assert pattern.Rows[row_index][0].Instrument == 1

    assert pattern.Rows[5][0].Note != pattern.Rows[6][0].Note
    assert pattern.Rows[6][0].Note != pattern.Rows[7][0].Note
    assert pattern.Rows[7][0].Note != pattern.Rows[8][0].Note

    for row_index in (10, 11, 12, 13):
        assert pattern.Rows[row_index][0].Note is not None

    for row_index in (15, 16, 17, 18):
        assert pattern.Rows[row_index][0].Note is not None

    for row_index in (20, 21, 22, 23):
        assert pattern.Rows[row_index][0].Note is not None

    for row_index in (25, 26, 27, 28):
        assert pattern.Rows[row_index][0].Note is not None

    for row_index in (30, 31):
        assert pattern.Rows[row_index][0].Note is not None


def test_supports_bend_values_in_compact_tuple_events() -> None:
    """Accept compact bend tokens directly inside a cell and emit an effect."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        [
            ["1b2", None],
            [None, None],
        ],
        ["E4", "A4"],
        7,
    )

    pattern = builder.build()

    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[0][0].Effect is not None
    assert pattern.Rows[0][0].EffectArg is not None


def test_supports_mixed_tokens_notes_and_none_across_strings() -> None:
    """Mix notes, compact effect tokens and empty cells across multiple strings."""
    builder = TablatureBuilder(lines_per_note=1)
    builder.add_tablature(
        [
            [3, "b2", None],
            [None, "1s2", 2],
            ["h2", 0, "1b2"],
        ],
        ["E4", "A4", "D4"],
        7,
    )

    pattern = builder.build()

    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    assert pattern.Rows[2][0].Effect is not None


def test_definitive_tablature_supports_large_mixed_syntax() -> None:
    """Build a large tablature that exercises notes, effects, chords, padding and multiple blocks together."""
    builder = TablatureBuilder(instrument_id=5, lines_per_note=1, bpm=160, max_rows=128)

    rows: List[Any] = [
        [None,                          0,                      "1b2",  None                       ],
        [{"fret": 3, "bend": 2},        None,                   "h2",   2                          ],
        [{"chord": [(0, 2), (1, 3)]},   "1s2",                   None,  None                       ],
        [4,                             None,                    None,  "b2"                       ],
        [None,                          {"fret": 5, "slide": 1}, None,  None                       ],
        [3,                             "b2",                    None,  "1h2"                      ],
        [None,                          None,                    0,     None                       ],
        [None,                          0,                       "1b2", 1                          ],
        [0,                             None,                    "s2",  {"fret": 4, "hammer_on": 2}],
        ["1b2",                         {"fret": 2, "bend": 1},  3,     None                       ],
        [None,                          None,                    None,  None                       ],
        [0,                             1,                       2,     3                          ],
    ]

    builder.add_tablature(
        tablature=rows,
        tuning=["E4", "A4", "D4", "G3"],
        fret_count=12,
        pre_note_effects={"volume_slide": 3},
        post_note_effects={"set_volume": 64},
    )

    builder.add_tablature(
        tablature=[
            ["1b2", None, 2,    "s2"                  ],
            [None,  1,    None, {"fret": 4, "bend": 1}],
            ["h2",  0,    None, None                  ],
        ],
        tuning=["E4", "A4", "D4", "G3"],
        fret_count=12,
    )

    pattern = builder.build()

    assert pattern is not None
    assert pattern.Rows[0][0].Note is not None
    assert pattern.Rows[1][0].Note is not None
    assert pattern.Rows[2][0].Note is not None
    assert pattern.Rows[2][0].Instrument == 5
    assert pattern.Rows[0][0].Instrument == 5
    assert pattern.Rows[1][0].Effect is not None
    assert pattern.Rows[1][0].EffectArg is not None

    populated_notes = [
        cell
        for row in pattern.Rows
        for cell in row
        if cell.Note is not None
    ]
    populated_effects = [
        cell
        for row in pattern.Rows
        for cell in row
        if cell.Effect is not None
    ]

    assert len(populated_notes) >= 12
    assert len(populated_effects) >= 4
    assert any(cell.Note is not None and cell.Effect is not None for cell in populated_notes)


def test_rejects_ambiguous_multi_value_tuple_slots() -> None:
    """Reject tuple-based slots that try to represent more than one note in a single position."""
    builder = TablatureBuilder(lines_per_note=1)
    with pytest.raises(ValueError):
        builder.add_tablature(
            [
                [
                    (3, 1, 0),
                    "b2", 
                    None
                ],
            ],
            ["E4", "A4", "D4"],
            7,
        )
    
