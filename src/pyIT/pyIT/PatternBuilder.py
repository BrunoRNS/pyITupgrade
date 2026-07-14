# -*- coding: utf-8 -*-
"""Helpers for constructing IT patterns from simple note sequences."""

from typing import Optional, Sequence

from .ITpattern import ITpattern


class PatternBuilder:
    """Build IT patterns from a sequence of note names."""

    def __init__(self, bpm: int = 180, lines_per_note: int = 4) -> None:
        """Initialize the builder with tempo and spacing settings.

        Args:
            bpm: Beats per minute value stored on the builder instance.
            lines_per_note: Number of pattern rows reserved for each note event.
        """
        self.bpm = bpm
        self.lines_per_note = lines_per_note

        self._semitones = {
            "C": 0,
            "C#": 1,
            "D": 2,
            "D#": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "G": 7,
            "G#": 8,
            "A": 9,
            "A#": 10,
            "B": 11,
        }

    def note_name_to_number(self, note_name: Optional[str]) -> Optional[int]:
        """Convert a note name into an IT-compatible note number.

        Args:
            note_name: A note such as ``C4``, ``F#5``, or ``DO``.

        Returns:
            The corresponding IT note number, or ``None`` if no note was given.
            Invalid values fall back to ``C-5`` (60).
        """
        if not note_name:
            return None

        clean_note = note_name.upper().replace("-", "")

        aliases = {
            "DO": "C5",
            "RE": "D5",
            "MI": "E5",
            "FA": "F5",
            "SOL": "G5",
            "LA": "A5",
            "SI": "B5",
        }
        if clean_note in aliases:
            clean_note = aliases[clean_note]

        try:
            if "#" in clean_note:
                pitch = clean_note[:2]
                octave = int(clean_note[2:])
            else:
                pitch = clean_note[0]
                octave = int(clean_note[1:])

            return (octave * 12) + self._semitones[pitch]
        
        except (KeyError, ValueError):
            return 60
        
    def pattern_len(self, note_sequence: Sequence[Optional[str]]) -> int:
        """Calculate the length of a pattern from a sequence of note names."""
        
        return len(note_sequence) * self.lines_per_note
    
    def last_index(self, note_sequence: Sequence[Optional[str]]) -> int:
        """Calculate the last index in a pattern from a sequence of note names."""
        
        return self.pattern_len(note_sequence) - self.lines_per_note

    def split_long_pattern(self, note_sequence: Sequence[Optional[str]]) -> Sequence[Sequence[Optional[str]]]:
        """Split a pattern into multiple chunks if it exceeds the 64-line limit."""
        
        return [note_sequence[i:i + 64] for i in range(0, len(note_sequence), 64)]
    
    def build_long_pattern(self, note_sequence: Sequence[Optional[str]], instrument_id: int = 1) -> Sequence[ITpattern]:
        """Build multiple IT patterns from a sequence of note names, optionally stopping early with Pattern Break.

        Args:
            note_sequence: Iterable of note names. ``None`` values produce empty rows.
            instrument_id: Instrument number assigned to populated note cells.

        Returns:
            A list of ``ITpattern`` instances with notes placed on channel 0.
        """
        
        slited_pattern = self.split_long_pattern(note_sequence)
        return [
            self.build_pattern(pattern, instrument_id) \
            for pattern in slited_pattern[:-1]] + \
            [
                self.build_pattern(
                    note_sequence=slited_pattern[-1],
                    instrument_id=instrument_id, 
                    stop_line=self.last_index(slited_pattern[-1])
                )
            ]

    def build_pattern(
        self, note_sequence: Sequence[Optional[str]], instrument_id: int = 1, stop_line: int|None = None
    ) -> ITpattern:
        """Create an IT pattern from a sequence of note names, optionally stopping early with Pattern Break.

        Args:
            note_sequence: Iterable of note names. ``None`` values produce empty rows.
            instrument_id: Instrument number assigned to populated note cells.
            stop_line: Optional line number to insert Pattern Break and stop the pattern early.

        Returns:
            An ``ITpattern`` instance with notes placed on channel 0.
        """
        pattern = ITpattern()
        current_line = 0

        for note in note_sequence:
            if current_line >= 64:
                print("[Warning] The note sequence exceeded the 64-line pattern limit and was truncated.")
                break

            if stop_line is not None and current_line == stop_line:
                note_cell = pattern.Rows[current_line][0]
                note_cell.Effect = 0x02
                note_cell.EffectArg = 0x00
                break

            if note is not None:
                note_number = self.note_name_to_number(note)
                note_cell = pattern.Rows[current_line][0]
                note_cell.Note = note_number
                note_cell.Instrument = instrument_id
                note_cell.Volume = 64

            current_line += self.lines_per_note

        return pattern
