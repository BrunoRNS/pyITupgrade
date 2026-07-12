from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union, cast

NoteLike = Union[int, None, str, Dict[str, Any], Tuple[Any, ...], List[Any]]
tablature_row = Sequence[NoteLike]

from .ITpattern import ITpattern
from .PatternBuilder import PatternBuilder


class TablatureBuilder:
    """Build IT patterns from guitar-like tablatures.

    The builder converts tablature rows into IT note events using a single
    pattern channel. When a row contains several active notes, they are played
    in rapid succession on consecutive rows, which emulates a fast arpeggiated
    execution while keeping the data compact.
    """

    _EFFECT_CODES: Dict[str, int] = {
        "volume_slide": 0x0A,
        "portamento_up": 0x01,
        "portamento_down": 0x02,
        "slide": 0x03,
        "bend": 0x04,
        "vibrato": 0x04,
        "tremolo": 0x07,
        "set_volume": 0x0C,
        "set_pan": 0x08,
        "set_speed": 0x0F,
        "delay": 0x0E,
        "hammer_on": 0x01,
        "hammer_off": 0x02,
    }

    def __init__(
        self,
        instrument_id: int = 1,
        lines_per_note: int = 4,
        bpm: int = 180,
        max_rows: int = 64,
    ) -> None:
        """Initialize the tablature builder.

        Args:
            instrument_id: Default instrument number assigned to generated notes.
            lines_per_note: Number of pattern rows consumed between beats.
            bpm: Tempo used by the underlying pattern builder.
            max_rows: Maximum number of rows allowed in the generated pattern.
        """
        self.instrument_id = instrument_id
        self.lines_per_note = max(1, lines_per_note)
        self.bpm = bpm
        self.max_rows = max_rows
        self._pattern_builder = PatternBuilder(bpm=bpm, lines_per_note=lines_per_note)
        self._pattern = ITpattern()
        self._current_row = 0
        self._queued_tablatures: List[Tuple[Tuple[Any, ...], List[str], int, Optional[int], Optional[Dict[str, int]], Optional[Dict[str, int]], int]] = []

    def set_bpm(self, bpm: int) -> None:
        """Update the BPM used by the builder and the underlying pattern builder."""
        if bpm <= 0:
            raise ValueError("bpm must be greater than zero.")
        self.bpm = bpm
        self._pattern_builder = PatternBuilder(bpm=bpm, lines_per_note=self.lines_per_note)

    def add_tablature(
        self,
        tablature: Sequence[tablature_row],
        tuning: Sequence[str],
        fret_count: int,
        instrument_id: Optional[int] = None,
        pre_note_effects: Optional[Dict[str, int]] = None,
        post_note_effects: Optional[Dict[str, int]] = None,
        bpm: Optional[int] = None,
    ) -> None:
        """Queue a tablature block for later assembly.

        Args:
            tablature: Rows of note events. Each row may contain per-string values,
                event dictionaries, or a list of note events for chords.
            tuning: List of note names describing the tuning of each string.
            fret_count: Maximum allowed fret value for validation.
            instrument_id: Optional override for the instrument number.
            pre_note_effects: Effects applied on the row immediately before the note.
            post_note_effects: Effects applied on the row immediately after the note.
            bpm: Optional BPM override for this tablature block.

        Raises:
            ValueError: If the tablature shape, tuning, or fret values are invalid.
        """
        if not tuning:
            raise ValueError("At least one string is required in the tuning.")
        if fret_count < 0:
            raise ValueError("fret_count must be non-negative.")

        normalized_rows: List[Tuple[Any, ...]] = []
        for row in tablature:
            normalized_rows.append(self._normalize_row(row, len(tuning), fret_count))

        effective_bpm = self.bpm if bpm is None else bpm
        self._queued_tablatures.append(
            (
                tuple(normalized_rows),
                [str(note_name) for note_name in tuning],
                fret_count,
                instrument_id,
                self._normalize_effects(pre_note_effects),
                self._normalize_effects(post_note_effects),
                effective_bpm,
            )
        )

    def build(self) -> ITpattern:
        """Assemble the queued tablatures into a single IT pattern.

        Returns:
            A populated IT pattern containing all queued tablature events.
        """
        self._pattern = ITpattern()
        self._current_row = 0

        for tablature, tuning, fret_count, instrument_id, pre_effects, post_effects, bpm in self._queued_tablatures:
            self.set_bpm(bpm)
            self._append_tablature(
                tablature=tablature,
                tuning=tuning,
                fret_count=fret_count,
                instrument_id=instrument_id if instrument_id is not None else self.instrument_id,
                pre_note_effects=pre_effects,
                post_note_effects=post_effects,
            )

        return self._pattern

    def _normalize_row(
        self,
        row: tablature_row,
        tuning_size: int,
        fret_count: int,
    ) -> Tuple[Any, ...]:
        """Normalize a tablature row into an internal list of note events."""
        if not isinstance(row, (tuple, list)):
            raise ValueError("Each tablature row must be a tuple or list of values.")
        if not row:
            return tuple()

        if len(row) > tuning_size:
            raise ValueError("Each tablature row must provide at most one slot per string.")

        if len(row) == tuning_size and all(value is None or isinstance(value, int) for value in row):
            return tuple(
                {"string": string_index, "fret": value}
                if value is not None
                else {"string": string_index, "fret": None}
                for string_index, value in enumerate(row)
            )

        if len(row) < tuning_size:
            row = tuple(list(row) + [None] * (tuning_size - len(row)))

        normalized_events: List[Dict[str, Any]] = []
        for index, item in enumerate(row):
            if isinstance(item, dict) and "chord" in item:
                chord_notes = cast(Mapping[str, Any], item).get("chord")
                if chord_notes is None:
                    raise ValueError("Chord values must be provided as a list or tuple.")
                chord_items = cast(Sequence[Any], chord_notes)
                for chord_item in chord_items:
                    normalized_events.append(self._normalize_event(chord_item, index, tuning_size, fret_count))
                continue

            if isinstance(item, (tuple, list)):
                sequence = cast(Sequence[Any], item)
                if len(sequence) == 2 and all(value is None or isinstance(value, int) for value in sequence):
                    normalized_events.append(self._normalize_event(item, index, tuning_size, fret_count))
                    continue
                if len(sequence) > 2:
                    raise ValueError("Each tablature row must provide at most one slot per string.")

            normalized_events.append(self._normalize_event(item, index, tuning_size, fret_count))
        return tuple(normalized_events)

    def _normalize_event(
        self,
        item: Any,
        default_string: int,
        tuning_size: int,
        fret_count: int,
    ) -> Dict[str, Any]:
        """Normalize a single tablature event into a dictionary representation."""
        if item is None:
            return {"string": default_string % max(1, tuning_size), "fret": None}

        if isinstance(item, dict):
            event: Dict[str, Any] = {}
            mapping = cast(Mapping[str, Any], item)
            for key, value in mapping.items():
                event[str(key)] = value
            string_index = event.get("string", default_string)
            event["string"] = self._coerce_string_index(string_index, tuning_size)
            event["fret"] = self._coerce_fret(event.get("fret"), fret_count)
            event["effects"] = self._normalize_effects(cast(Optional[Dict[str, int]], event.get("effects"))) or {}
            for effect_name in ("bend", "slide", "hammer_on", "hammer_off"):
                if effect_name in event and event[effect_name] is not None:
                    event["effects"][effect_name] = int(event[effect_name])
            return event

        if isinstance(item, str):
            parsed_token = self._parse_token(item)
            if parsed_token is not None:
                kind, value = parsed_token
                if kind == "bend":
                    return {
                        "string": self._coerce_string_index(default_string, tuning_size),
                        "fret": self._coerce_fret(value[0], fret_count) if value[0] is not None else None,
                        "effects": {"bend": value[1]},
                    }
                if kind == "slide":
                    return {
                        "string": self._coerce_string_index(default_string, tuning_size),
                        "fret": self._coerce_fret(value[0], fret_count) if value[0] is not None else None,
                        "effects": {"slide": value[1]},
                    }
                if kind == "hammer":
                    return {
                        "string": self._coerce_string_index(default_string, tuning_size),
                        "fret": self._coerce_fret(value[0], fret_count) if value[0] is not None else None,
                        "effects": {"hammer_on": value[1]},
                    }
            if item.isdigit():
                return {
                    "string": self._coerce_string_index(default_string, tuning_size),
                    "fret": self._coerce_fret(int(item), fret_count),
                    "effects": {},
                }

        if isinstance(item, (tuple, list)):
            sequence = cast(Sequence[Any], item)
            if len(sequence) >= 1 and all(value is None or isinstance(value, int) or isinstance(value, str) for value in sequence):
                if len(sequence) == 1:
                    if isinstance(sequence[0], str):
                        parsed_token = self._parse_token(sequence[0])
                        if parsed_token is not None:
                            kind, value = parsed_token
                            if kind == "bend":
                                return {
                                    "string": self._coerce_string_index(default_string, tuning_size),
                                    "fret": self._coerce_fret(value[0], fret_count) if value[0] is not None else None,
                                    "effects": {"bend": value[1]},
                                }
                            if kind == "slide":
                                return {
                                    "string": self._coerce_string_index(default_string, tuning_size),
                                    "fret": self._coerce_fret(value[0], fret_count) if value[0] is not None else None,
                                    "effects": {"slide": value[1]},
                                }
                            if kind == "hammer":
                                return {
                                    "string": self._coerce_string_index(default_string, tuning_size),
                                    "fret": self._coerce_fret(value[0], fret_count) if value[0] is not None else None,
                                    "effects": {"hammer_on": value[1]},
                                }
                    return {
                        "string": self._coerce_string_index(default_string, tuning_size),
                        "fret": self._coerce_fret(sequence[0], fret_count),
                        "effects": {},
                    }
                if len(sequence) == 2 and all(value is None or isinstance(value, int) for value in sequence):
                    return {
                        "string": self._coerce_string_index(default_string, tuning_size),
                        "fret": self._coerce_fret(sequence[0], fret_count),
                        "effects": {"bend": sequence[1]} if sequence[1] is not None else {},
                    }
                if len(sequence) == 3 and all(value is None or isinstance(value, int) for value in sequence):
                    return {
                        "string": self._coerce_string_index(default_string, tuning_size),
                        "fret": self._coerce_fret(sequence[0], fret_count),
                        "effects": {"bend": sequence[2]} if sequence[2] is not None else {},
                    }

        if isinstance(item, int):
            return {
                "string": self._coerce_string_index(default_string, tuning_size),
                "fret": self._coerce_fret(item, fret_count),
                "effects": {},
            }

        raise ValueError("Unsupported tablature event format.")

    def _parse_token(self, token: str) -> Optional[Tuple[str, Tuple[Optional[int], int]]]:
        """Parse compact tokens such as 'b2', '1b2', 's2' or 'h2'."""
        token = token.strip().lower()
        if not token:
            return None
        if token.startswith("b") and token[1:].isdigit():
            return "bend", (None, int(token[1:]))
        if "b" in token:
            prefix, _, suffix = token.partition("b")
            if prefix.isdigit() and suffix.isdigit():
                return "bend", (int(prefix), int(suffix))
        if token.startswith("s") and token[1:].isdigit():
            return "slide", (None, int(token[1:]))
        if "s" in token:
            prefix, _, suffix = token.partition("s")
            if prefix.isdigit() and suffix.isdigit():
                return "slide", (int(prefix), int(suffix))
        if token.startswith("h") and token[1:].isdigit():
            return "hammer", (None, int(token[1:]))
        if "h" in token:
            prefix, _, suffix = token.partition("h")
            if prefix.isdigit() and suffix.isdigit():
                return "hammer", (int(prefix), int(suffix))
        return None

    def _coerce_string_index(self, string_index: Any, tuning_size: int) -> int:
        """Validate and normalize a string index."""
        if not isinstance(string_index, int):
            string_index = int(string_index)
        if not 0 <= string_index < tuning_size:
            raise ValueError("String index is out of range for the configured tuning.")
        return string_index

    def _coerce_fret(self, fret: Any, fret_count: int) -> Optional[int]:
        """Validate and normalize a fret value."""
        if fret is None:
            return None
        if not isinstance(fret, int):
            fret = int(fret)
        if not 0 <= fret <= fret_count:
            raise ValueError("Fret values must be between 0 and the configured fret count.")
        return fret

    def _append_tablature(
        self,
        tablature: Sequence[Tuple[Any, ...]],
        tuning: Sequence[str],
        fret_count: int,
        instrument_id: int,
        pre_note_effects: Optional[Dict[str, int]],
        post_note_effects: Optional[Dict[str, int]],
    ) -> None:
        """Append a single tablature block to the current pattern."""
        for row in tablature:
            if self._current_row >= self.max_rows:
                return

            events: List[Dict[str, Any]] = []
            for event in row:
                if isinstance(event, dict):
                    event_data = cast(Dict[str, Any], event)
                    if event_data.get("fret") is not None:
                        events.append(event_data)
            if not events:
                self._current_row += self.lines_per_note
                continue

            base_row = self._current_row
            for event_offset, event in enumerate(events):
                note_row = base_row + event_offset
                if note_row >= self.max_rows:
                    break

                self._apply_effects(note_row, pre_note_effects, clear_note=True)
                self._set_note(
                    row_index=note_row,
                    fret=event["fret"],
                    tuning=tuning[event["string"] : event["string"] + 1],
                    fret_count=fret_count,
                    instrument_id=instrument_id,
                )
                self._apply_note_effects(note_row, cast(Dict[str, int], event.get("effects", {})))
                self._apply_note_effects(note_row + 1, cast(Dict[str, int], event.get("effects", {})))
                self._apply_effects(note_row + 1, post_note_effects, clear_note=True)

            self._current_row += self.lines_per_note

    def _set_note(
        self,
        row_index: int,
        fret: int,
        tuning: Sequence[str],
        fret_count: int,
        instrument_id: int,
    ) -> None:
        """Populate a pattern row with a note derived from the fret value."""
        if row_index >= self.max_rows:
            return

        note_number = self._fret_to_note_number(fret, tuning, fret_count)
        note_cell = self._pattern.Rows[row_index][0]
        note_cell.Note = note_number
        note_cell.Instrument = instrument_id
        note_cell.Volume = 64

    def _apply_note_effects(self, row_index: int, effects: Optional[Dict[str, int]]) -> None:
        """Apply per-note effect data to a pattern row."""
        if row_index >= self.max_rows or not effects:
            return

        note_cell = self._pattern.Rows[row_index][0]
        for effect_name, effect_arg in effects.items():
            effect_code = self._resolve_effect_code(effect_name)
            if effect_code is None:
                continue
            note_cell.Effect = effect_code
            note_cell.EffectArg = effect_arg & 0xFF
            break

    def _apply_effects(self, row_index: int, effects: Optional[Dict[str, int]], clear_note: bool) -> None:
        """Place effect-only rows in the pattern."""
        if row_index >= self.max_rows or not effects:
            return

        note_cell = self._pattern.Rows[row_index][0]
        if clear_note:
            note_cell.Note = None
            note_cell.Instrument = None
            note_cell.Volume = None

        for effect_name, effect_arg in effects.items():
            effect_code = self._resolve_effect_code(effect_name)
            if effect_code is None:
                continue
            note_cell.Effect = effect_code
            note_cell.EffectArg = effect_arg & 0xFF

    def _resolve_effect_code(self, effect_name: str) -> Optional[int]:
        """Resolve a human-friendly effect name into an IT effect code."""
        normalized_name = effect_name.strip().lower().replace("-", "_")
        return self._EFFECT_CODES.get(normalized_name)

    def _normalize_effects(self, effects: Optional[Dict[str, int]]) -> Optional[Dict[str, int]]:
        """Normalize raw effect dictionaries into a safe form."""
        if not effects:
            return None
        normalized: Dict[str, int] = {}
        for effect_name, effect_arg in effects.items():
            normalized[str(effect_name)] = int(effect_arg) & 0xFF
        return normalized

    def _fret_to_note_number(self, fret: int, tuning: Sequence[str], fret_count: int) -> Optional[int]:
        """Convert a fret position into an IT note number using the tuning."""
        if fret_count < 0:
            raise ValueError("fret_count must be non-negative.")
        if not tuning:
            raise ValueError("At least one string is required in the tuning.")

        base_note = self._pattern_builder.note_name_to_number(tuning[0])
        if base_note is None:
            return None
        return base_note + fret
