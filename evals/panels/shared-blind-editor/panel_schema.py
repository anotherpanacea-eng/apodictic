#!/usr/bin/env python3
"""Closed response schema shared by the panel packet builder and compiler."""

ARGUMENT_UNITS = ("A01", "A02", "A03", "A04", "A05")
FICTION_UNITS = ("F01", "F02", "F03", "F04", "F05", "F06", "F07")

LAYER = ("CLAIM", "SUPPORT", "WARRANT", "SCOPE", "BURDEN", "OBJECTION", "NONE")
TARGET = ("CLAIM", "SUPPORT", "WARRANT", "SCOPE", "BURDEN", "OBJECTION",
          "DEFINITION", "AUDIENCE", "IMPLEMENTATION", "NONE")
DEPENDENCY = ("BEFORE_SUPPORT", "BEFORE_SCOPE", "BEFORE_OBJECTION",
              "BEFORE_IMPLEMENTATION", "INDEPENDENT", "NONE")
VERDICT = ("WARRANTED", "UNCONVENTIONAL-BUT-WARRANTED", "UNWARRANTED")
FLAG_PRESENCE = ("NONE_REGISTERED", "FLAG_PRESENT")
FLAG_TYPES = ("CONTESTABLE", "UNEARNED", "OVERLOADED", "EXTERNAL-VERIFY", "DEFINITIONAL")
EXPERTISE = {"GENERAL": "1", "MIXED": "2", "SPECIALIST": "3"}
RECEPTIVITY = {"HOSTILE": "1", "MIXED": "2", "SYMPATHETIC": "3"}
CONSEQUENCE = {"LOW": "1", "MEDIUM": "2", "HIGH": "3"}
BOUNDARY_PATTERN = ("FORMAL_DIVISIONS", "VISITATION_OR_ENCOUNTER", "CAUSAL_TURNS",
                    "HYBRID", "OTHER_RECURRENT", "NO_STABLE_PATTERN")
ARC = ("DENIAL_STAGED_CONFRONTATION_REVERSAL", "STEADY_GROWTH", "FALL",
       "CIRCULAR_RETURN", "FLAT_NO_REVERSAL", "OTHER")
YES_NO = ("NO", "YES")

FIELDS = (
    "editor_id", "unit_id", "domain", "recognized",
    "gt2_layer", "gt2_locus_1", "gt2_locus_2",
    "gt4_expertise", "gt4_receptivity", "gt4_consequence",
    "gt5_family", "gt5_locus_1", "gt5_locus_2",
    "gt6_target", "gt6_locus_1", "gt6_locus_2", "gt6_dependency",
    "gt7_verdict", "gt8_presence", "gt8_locus_1", "gt8_locus_2", "gt8_flag_types",
    "fgt1_movement_count", "fgt1_boundary_1", "fgt1_boundary_2",
    "fgt1_boundary_3", "fgt1_boundary_4", "fgt1_boundary_5",
    "fgt1_boundary_6", "fgt1_boundary_7", "fgt1_boundary_8",
    "fgt1_boundary_pattern", "fgt5_arc", "notes",
)


def normalized_locus(paragraph_id: str, paragraph_count: int) -> str:
    """Map a closed paragraph id to the preregistered 0..100 ordinal scale."""
    if paragraph_id == "":
        return ""
    try:
        value = int(paragraph_id)
    except ValueError as exc:
        raise ValueError(f"paragraph id must be an integer, got {paragraph_id!r}") from exc
    if not 1 <= value <= paragraph_count:
        raise ValueError(f"paragraph id {value} outside 1..{paragraph_count}")
    if paragraph_count == 1:
        return "0"
    return str(round(100 * (value - 1) / (paragraph_count - 1)))
