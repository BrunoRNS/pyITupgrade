from .test_pattern import (
    test_note_name_to_number_supports_common_note_names,
    test_note_name_to_number_supports_portuguese_aliases,
    test_note_name_to_number_falls_back_to_middle_c_for_invalid_names,
    test_build_pattern_places_notes_on_expected_rows_and_keeps_instrument,
    test_build_pattern_respects_lines_per_note_spacing,
    test_build_pattern_skips_none_entries_and_keeps_the_pattern_dense,
    test_build_pattern_truncates_sequences_beyond_the_pattern_limit,
    test_build_pattern_matches_the_reference_sequence_shape,
)

__all__ = [
    "test_note_name_to_number_supports_common_note_names",
    "test_note_name_to_number_supports_portuguese_aliases",
    "test_note_name_to_number_falls_back_to_middle_c_for_invalid_names",
    "test_build_pattern_places_notes_on_expected_rows_and_keeps_instrument",
    "test_build_pattern_respects_lines_per_note_spacing",
    "test_build_pattern_skips_none_entries_and_keeps_the_pattern_dense",
    "test_build_pattern_truncates_sequences_beyond_the_pattern_limit",
    "test_build_pattern_matches_the_reference_sequence_shape",
]
