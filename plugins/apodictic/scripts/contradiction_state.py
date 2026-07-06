#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared contradiction-state axis for the APODICTIC bible validators (world-bible + continuity-bible).

A self-contradiction is a *fact-state*, not an editorial defect — it must NOT be forced onto the
Must/Should/Could severity scale (the design's binding D1). This module owns the ONE axis both bible
Contradiction Ledgers share, orthogonal to severity, exactly as Legal Risk's escalation tier and
Content Advisory's intensity are orthogonal to it:

  consistent   no literal collision (no ledger row is written for it — including the deliberate
               conservatism that IMPLIED conflicts don't fire).
  conflicting  a literal collision, un-overridden — "these two stated values cannot both hold."
  apparent     a collision with a matching `<!-- override: … -->` — fired but marked intentional /
               explained in-world ("looks conflictual, but the author staged it").

The state is **mechanically computed, never judged** (§D4). The model still authors the fact
EXTRACTION only; the validator DERIVES the state deterministically from the literal collision + the
override presence, and the X1 firewall proves the register never grows a severity token or a
`apodictic:finding` block. This mirrors setup_payoff_checks.derive_state (the sibling fact-state axis)
byte-for-byte in posture.

Both bibles import this; NO new schema — the `State` column rides the existing plain-markdown
`## Contradiction Ledger` table, parsed like continuity_bible's bespoke C3 table parse. The two bibles
differ only in which override slugs mark a pair intentional (world-bible: world-rule/world-cost/
world-geo, already live; continuity-bible: the new `bible-contradiction` slug) — each validator passes
its own `overridden` flag; this module owns the truth table, the enum, the column parse, and the X1
regex so all three live in ONE place.

Not an AGG_VALIDATORS entry (a shared helper, like override_marker / apodictic_artifacts); it carries a
`--self-test` for direct coverage of the truth table + the parse + the firewall regex.
See docs/worldbuilding-bible.md / docs/continuity-bible.md (§State axis).
"""
import re
import sys

from severity_vocab import SEVERITY_TOKEN_RE  # SSoT: the editorial Must/Should/Could-Fix leak token

# The three states, in the order the derivation prefers them. A `consistent` row is never WRITTEN
# (no collision -> no ledger row), so in practice only `conflicting` / `apparent` appear in a real
# ledger; `consistent` is still a valid enum token so an author who explicitly records a resolved-clean
# row is not forced to lie. `derive_state` returns it for the no-collision case.
VALID_STATES = ("conflicting", "apparent", "consistent")

# X1 firewall — the Contradiction Ledger is a fact register, not a defect list. The pattern is the
# shared severity_vocab SSoT (M8), the Content-Advisory A3 firewall applied here; an apodictic:finding
# block is caught by the caller's parsed-block check (so a file that merely NAMES the token in prose
# still FAILs — severity must never leak into the register).
_SEVERITY_RE = SEVERITY_TOKEN_RE


def derive_state(collides, overridden):
    """The §D4 truth table — the SINGLE source of a contradiction's derived state.

      no collision                 -> consistent   (nothing fired)
      collision + matching override -> apparent     (fired, marked intentional)
      collision, no override       -> conflicting  (fired, live)

    `collides` / `overridden` are booleans the caller computes mechanically (a literal fact collision;
    a live `<!-- override: <slug> <id>/<id> -->` marker naming the pair). No model judgment enters
    here — the register never overrides the derivation."""
    if not collides:
        return "consistent"
    return "apparent" if overridden else "conflicting"


def severity_leak(text):
    """True if the register carries an editorial Must/Should/Could-Fix token (the X1 severity half).
    The finding-block half is the caller's parsed-block check (`_has_block(text, "finding")`), kept
    there so the parse routes through each validator's own apodictic_artifacts import (M2 hygiene)."""
    return _SEVERITY_RE.search(text or "") is not None


# ------------------------------------------------------- the State column parse

def _is_alignment_row(cells):
    return all(set(c) <= set("-: ") for c in cells)


def state_rows(text, id_re):
    """Parse each DATA row under a `## Contradiction Ledger` into (ids, state_token, cells).

    A bespoke plain-markdown table parse — the ledger is NOT an apodictic:* block — mirroring
    continuity_bible.contradiction_rows (same section-scan + alignment/header skip), extended to also
    pull the `State` column. `id_re` is the caller's fact-id pattern (`CF-[0-9]+` for continuity,
    `WF-[0-9]+` for world). Returns, per data row:
      * ids          — the fact ids the row references (via `id_re`), in appearance order.
      * state_token  — the value of the `State` column, lowercased and stripped, or None if the table
                       has no State column (a pre-axis ledger — the caller treats None as "unstated").
      * cells        — the raw stripped cells (so a caller can cite the row for a diagnostic).

    The State column is located by a header cell whose lowercased text is exactly `state` (not a
    substring — so a `Statement`/`Restated` column never masquerades as it). Header detection reuses
    continuity_bible's Entity+Attribute heuristic AND the explicit `state` header, so both bibles'
    differently-shaped headers (world: Subject/Arm/…; continuity: Entity/Attribute/…) are recognized."""
    out, in_section, state_idx, header_seen = [], False, None, False
    for ln in (text or "").split("\n"):
        if re.match(r"^##\s+.*Contradiction\s+Ledger", ln, re.IGNORECASE):
            in_section, state_idx, header_seen = True, None, False
            continue
        if in_section and re.match(r"^##\s", ln):
            break  # next section ends the ledger
        if not in_section or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if _is_alignment_row(cells):
            continue
        low = [c.lower() for c in cells]
        is_header = (not header_seen) and (
            "state" in low
            or (any("entity" == c or "subject" == c for c in low)
                and any(c in ("attribute", "arm", "conflicting facts") for c in low)))
        if is_header:
            header_seen = True
            for i, c in enumerate(low):
                if c == "state":
                    state_idx = i
            continue
        ids = id_re.findall(ln)
        token = None
        if state_idx is not None and state_idx < len(cells):
            raw = cells[state_idx].strip().lower()
            token = raw if raw else None
        out.append((ids, token, cells))
    return out


def has_state_column(text):
    """True iff a `## Contradiction Ledger` table carries a `State` column (an exact-`state` header
    cell, the same detection state_rows uses to locate `state_idx`). A caller uses this WITH the row
    count to distinguish a *pre-axis* ledger (data rows but no State column — the additive column was
    never added) from a State-axis ledger whose cells merely happen to be blank (token=None per row):
    only the former warrants the loud pre-axis WARN. Mirrors the state_rows section-scan + header
    detection exactly so the two never disagree."""
    in_section, header_seen = False, False
    for ln in (text or "").split("\n"):
        if re.match(r"^##\s+.*Contradiction\s+Ledger", ln, re.IGNORECASE):
            in_section, header_seen = True, False
            continue
        if in_section and re.match(r"^##\s", ln):
            break
        if not in_section or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if _is_alignment_row(cells):
            continue
        low = [c.lower() for c in cells]
        is_header = (not header_seen) and (
            "state" in low
            or (any("entity" == c or "subject" == c for c in low)
                and any(c in ("attribute", "arm", "conflicting facts") for c in low)))
        if is_header:
            header_seen = True
            return "state" in low
    return False


def check_row_states(rows, derived_for):
    """Cross-check each parsed ledger row's author-written `State` token against the mechanically
    derived state. `rows` is state_rows(...) output; `derived_for(ids)` returns EITHER the derived
    state string ('conflicting' | 'apparent' | 'consistent') OR a `(collides, overridden)` bool tuple
    (routed through derive_state here) for a row's ids — the caller computes collision + override.
    Returns a list of X1 error strings:

      * a State token that is not one of VALID_STATES (a bad enum);
      * a State token that DISAGREES with the derivation (an author-asserted state that contradicts
        the fire/override reality — the register never overrides the derivation);
      * a `consistent` row that is nonetheless WRITTEN (a consistent fact needs no ledger row; writing
        one is either a stray row or a mislabel).

    A row with no State column token (None) is NOT flagged here — a pre-axis ledger predates the column
    and is not required to carry it (the column is additive); the caller decides whether to require it.
    """
    errs = []
    for ids, token, cells in rows:
        if token is None:
            continue
        pair = "+".join(ids) if ids else "<no ids>"
        if token not in VALID_STATES:
            errs.append("X1 State enum: ledger row [%s] has State %r, not one of %s"
                        % (pair, token, ", ".join(VALID_STATES)))
            continue
        derived = derived_for(ids)
        # Tolerate both caller conventions: a derived-state STRING (the caller already ran
        # derive_state with its own collision/override booleans) or a raw `(collides, overridden)`
        # tuple (routed through the truth table here). Both resolve to a state string.
        if isinstance(derived, tuple):
            derived = derive_state(*derived)
        if token == "consistent":
            errs.append("X1 State agreement: ledger row [%s] is labeled `consistent`, but a "
                        "consistent fact needs no Contradiction-Ledger row (a written row is a live "
                        "collision — `conflicting` or `apparent`)" % pair)
        elif derived is not None and token != derived:
            errs.append("X1 State agreement: ledger row [%s] declares State %r but the fire/override "
                        "state derives %r — the author-asserted state disagrees with the mechanical "
                        "derivation (the register never overrides the derivation)" % (pair, token, derived))
    return errs


# ------------------------------------------------------- self-test

def _self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # derive_state — the §D4 truth table
    chk("derive_no_collision_consistent", derive_state(False, False) == "consistent")
    chk("derive_no_collision_overridden_still_consistent", derive_state(False, True) == "consistent")
    chk("derive_collision_conflicting", derive_state(True, False) == "conflicting")
    chk("derive_collision_overridden_apparent", derive_state(True, True) == "apparent")

    # severity_leak — the X1 severity half
    chk("severity_leak_fires", severity_leak("SP-03 is a Must-Fix.") is True)
    chk("severity_leak_should", severity_leak("a Should-Fix here") is True)
    chk("severity_leak_clean", severity_leak("both values recorded, surfaced not resolved") is False)

    CF = re.compile(r"\bCF-[0-9]+\b")
    WF = re.compile(r"\bWF-[0-9]+\b")

    # state_rows — continuity-shaped header (Entity | Attribute | Conflicting facts | State | Note)
    cont = ("## Contradiction Ledger\n\n"
            "| Entity | Attribute | Conflicting facts | State | Note |\n"
            "|---|---|---|---|---|\n"
            "| Mara | age | CF-03, CF-04 | conflicting | 30 vs 32 |\n"
            "| Jon | height | CF-05, CF-06 | apparent | staged reveal, overridden |\n")
    rows = state_rows(cont, CF)
    chk("cont_two_rows", len(rows) == 2)
    chk("cont_row0_ids_and_state", rows[0][0] == ["CF-03", "CF-04"] and rows[0][1] == "conflicting")
    chk("cont_row1_state_apparent", rows[1][1] == "apparent")

    # state_rows — world-shaped header (Subject | Arm | Conflicting facts | State | Author's note)
    world = ("## Contradiction Ledger\n\n"
             "| Subject | Arm | Conflicting facts | State | Author's note |\n"
             "|---|---|---|---|---|\n"
             "| blood-magic | rule (WB-R1) | WF-02, WF-03 | apparent | staged reveal, override world-rule |\n")
    wrows = state_rows(world, WF)
    chk("world_one_row", len(wrows) == 1 and wrows[0][0] == ["WF-02", "WF-03"])
    chk("world_state_apparent", wrows[0][1] == "apparent")

    # a `State`-substring header column (`Statement`) must NOT be read as the State column
    decoy = ("## Contradiction Ledger\n\n"
             "| Entity | Attribute | Conflicting facts | Statement |\n"
             "|---|---|---|---|\n"
             "| Mara | age | CF-03, CF-04 | both ages recorded |\n")
    drows = state_rows(decoy, CF)
    chk("state_substring_not_column", drows[0][1] is None)

    # a pre-axis ledger (no State column) yields token=None (not required to carry it)
    preaxis = ("## Contradiction Ledger\n\n"
               "| Entity | Attribute | Conflicting facts | Note |\n"
               "|---|---|---|---|\n"
               "| Mara | age | CF-03, CF-04 | 30 vs 32 |\n")
    chk("preaxis_token_none", state_rows(preaxis, CF)[0][1] is None)

    # has_state_column — distinguishes a State-axis ledger from a pre-axis one (the adopted-P3
    # loud-absence WARN keys on this). A blank-celled State column is STILL a State column (has it);
    # a decoy `Statement` header is NOT the State column; a pre-axis ledger has none.
    chk("has_state_column_true", has_state_column(cont) is True)
    chk("has_state_column_preaxis_false", has_state_column(preaxis) is False)
    chk("has_state_column_statement_decoy_false", has_state_column(decoy) is False)
    chk("has_state_column_no_ledger_false", has_state_column("# no ledger here\n") is False)

    # the ledger section ends at the next ## heading
    scoped = cont + "\n## Notes\n\n| not | a | ledger | row | here |\n"
    chk("section_scoped", len(state_rows(scoped, CF)) == 2)

    # check_row_states — agreement, enum, consistent-written, disagreement
    # derived_for returns the derived state STRING
    def derived_all_conflicting(ids):
        return "conflicting"

    def derived_apparent_for_jon(ids):
        return "apparent" if "CF-05" in ids else "conflicting"

    chk("agreement_clean",
        check_row_states(state_rows(cont, CF), derived_apparent_for_jon) == [])
    # bad enum token
    bad_enum = cont.replace("| conflicting |", "| resolved |")
    errs = check_row_states(state_rows(bad_enum, CF), derived_apparent_for_jon)
    chk("bad_enum_flagged", any("X1 State enum" in e for e in errs))
    # author says apparent but derivation says conflicting (override absent) -> disagreement
    mismatch = cont.replace("| conflicting |", "| apparent |")
    errs = check_row_states(state_rows(mismatch, CF), derived_all_conflicting)
    chk("author_asserted_disagreement_flagged", any("X1 State agreement" in e for e in errs))
    # a `consistent` row is written -> flagged (consistent needs no row)
    consist = cont.replace("| conflicting |", "| consistent |")
    errs = check_row_states(state_rows(consist, CF), derived_all_conflicting)
    chk("consistent_row_written_flagged",
        any("X1 State agreement" in e and "needs no" in e for e in errs))
    # a None-token (pre-axis) row is not flagged
    chk("preaxis_row_not_flagged",
        check_row_states(state_rows(preaxis, CF), derived_all_conflicting) == [])
    # tuple-returning derived_for is tolerated (collides, overridden)
    chk("tuple_derived_for_ok",
        check_row_states(state_rows(cont, CF),
                         lambda ids: (True, "CF-05" in ids)) == [])

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return _self_test()
    print("contradiction_state.py — shared helper (no CLI surface); run with --self-test.")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
