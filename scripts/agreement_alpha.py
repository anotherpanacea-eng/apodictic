#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Krippendorff's alpha inter-rater reliability CLI (pure stdlib).

Backs `validate.sh agreement-alpha <ratings.csv> [--metric nominal|ordinal]`. This is the
mechanical half of the Argument (and, by reference, Fiction) Benchmark's agreement-as-license
promotion workflow: a provisional ground-truth anchor is promoted to a gate-licensed status only
when a >=3-editor panel's measured agreement clears a pre-registered threshold (the psychometric
frame — inter-rater agreement LICENSES a label, it never scores the engine). It ships BEFORE any
human panel data exists so the promotion round is analysis-ready and the alpha number is computed
by audited, self-tested code rather than an ad-hoc notebook.

Method — Krippendorff's alpha-reliability (nominal + ordinal difference metrics):

    alpha = 1 - Do/De

  where, over the coincidence matrix o[c][k] (each within-unit ordered pair of values contributes
  1/(m_u - 1) for a unit with m_u pairable values; units with < 2 values contribute nothing):

    Do = sum over all ordered class pairs (c,k) of  o[c][k] * delta2(c,k)
    De = (1/(n-1)) * sum over all ordered class pairs (c,k) of  n_c * n_k * delta2(c,k)

  n   = sum of all o[c][k]  (total pairable values)
  n_c = sum_k o[c][k]       (coincidence-matrix marginal for value class c)

  Difference functions:
    nominal:  delta2(c,k) = 0 if c == k else 1
    ordinal:  delta2(c,k) = ( sum_{g in [c..k]} n_g  -  (n_c + n_k)/2 )^2   (Krippendorff's
              ordinal metric; g ranges over value classes sorted numerically between c and k
              inclusive; requires numeric values)

  Degenerate case: De = 0 (a single value class occurs — every rater gave the one same value
  across all units) leaves alpha = 0/0 undefined. The tool prints `alpha=UNDEFINED (D_e=0)` with
  a WARN and the licensing default treats it as NOT clearing any threshold (a constant column is
  no evidence of discriminative agreement).

Bootstrap 95% CI (pinned contract):
  >= 1000 resamples over UNITS (resample the units with replacement, recompute alpha per resample
  — the Hayes & Krippendorff (2007) unit-level scheme), default 1000, `--resamples` may only RAISE
  the floor; a fixed default seed (`--seed`, default pinned below) so two auditors reproduce the
  same CI byte-for-byte; percentile 95% interval (2.5 / 97.5) over the resamples whose alpha is
  defined. The seeded generator is CPython's Mersenne Twister via `random.Random`, whose
  `getrandbits`-backed integer draws are stable across CPython versions (reproducible CI).

Licensing (pre-registered thresholds; applied by the M2 round, not by this tool): license on the
CI LOWER BOUND clearing the threshold, not the point estimate (at small n a point estimate alone
can falsely promote on resampling noise). alpha >= .800 -> panel-licensed; .667 <= alpha < .800 ->
provisional; alpha < .667 -> low-agreement. See docs/argument-benchmark-spec.md.
SMALL-n WARNING: with ~10 units per dimension alpha is unstable; the CI lower-bound rule trades
slower promotion for no false license. Read the CI, not just the point estimate.

Input CSV: a tidy file with a REQUIRED `rater,unit,value` header row (exact match after
whitespace strip; missing or wrong header -> ERROR). Parsed with the stdlib `csv` module (standard
quoting). A blank `value` = missing data. A malformed row (column count != 3, or an empty
`rater`/`unit`) -> ERROR naming the line number; never silently skipped.

Sources:
  Krippendorff, K. (2011/2013). "Computing Krippendorff's Alpha-Reliability." (nominal + ordinal
    difference functions; the coincidence-matrix formulation; the worked example self-tested below.)
  Hayes, A. F., & Krippendorff, K. (2007). "Answering the Call for a Standard Reliability Measure
    for Coding Data." Communication Methods and Measures, 1(1), 77-89. (the unit-level bootstrap CI.)

Output keeps the legacy WARN: / ERROR: / OK: / FAILED: prefixes and exit codes (0 ok/warn,
1 data-contract failure, 2 usage/input error) so it slots into --self-test-all alongside the
other self-testable validators.
"""

import csv
import io
import math
import random
import sys

_DEFAULT_SEED = 20260709      # pinned so two auditors reproduce the same CI byte-for-byte
_DEFAULT_RESAMPLES = 1000     # Hayes & Krippendorff (2007) floor; --resamples may only raise it
_PANEL_FLOOR = 3              # panel-licensing needs a >=3-editor panel (docs/argument-benchmark-spec.md
                             # §GT schema: "panel-licensed | Promoted by measured >=3-editor agreement")
_METRICS = ("nominal", "ordinal")

_REQUIRED_HEADER = ["rater", "unit", "value"]


# --------------------------------------------------------------------------
# CSV parsing
# --------------------------------------------------------------------------

def read_ratings(text):
    """Parse tidy `rater,unit,value` CSV text.

    Returns (rows, error). On success rows is a list of (rater, unit, value_or_None) and error is
    None. On failure rows is None and error is a single `ERROR: ...` string. A blank value is
    missing data (None); an empty rater/unit or a wrong column count is a malformed-row ERROR that
    names the file line number.
    """
    reader = csv.reader(io.StringIO(text))
    header_seen = False
    rows = []
    seen_keys = set()
    for raw in reader:
        # Skip truly blank lines (csv yields [] for an empty line; tolerate a lone whitespace cell).
        if len(raw) == 0 or (len(raw) == 1 and raw[0].strip() == ""):
            continue
        ln = reader.line_num
        if not header_seen:
            norm = [c.strip() for c in raw]
            if norm != _REQUIRED_HEADER:
                return None, ("ERROR: line %d: required header row `rater,unit,value` missing or "
                              "wrong (got %r)." % (ln, ",".join(raw)))
            header_seen = True
            continue
        if len(raw) != 3:
            return None, ("ERROR: line %d: malformed row — expected exactly 3 columns "
                          "(rater,unit,value), got %d." % (ln, len(raw)))
        rater, unit, value = raw[0].strip(), raw[1].strip(), raw[2].strip()
        if rater == "" or unit == "":
            return None, ("ERROR: line %d: malformed row — `rater` and `unit` may not be empty."
                          % ln)
        # A literal repeat of the header row mid-file is unambiguous evidence of concatenated
        # CSVs — reject loudly rather than ingest a phantom rater named "rater".
        if [rater, unit, value] == _REQUIRED_HEADER:
            return None, ("ERROR: line %d: repeated header row `rater,unit,value` mid-file — "
                          "looks like two CSVs concatenated; merge the data rows under one "
                          "header." % ln)
        # A duplicate (rater, unit) key silently manufactures pairable self-agreement (rater
        # identity is ignored in pairing), shifting alpha on a LICENSING input from the most
        # plausible panel data-entry accident (a double-pasted row). Loud ERROR, never silent.
        key = (rater, unit)
        if key in seen_keys:
            return None, ("ERROR: line %d: duplicate rating — rater %r already rated unit %r "
                          "earlier in the file; one rating per (rater, unit)." % (ln, rater, unit))
        seen_keys.add(key)
        rows.append((rater, unit, value if value != "" else None))
    if not header_seen:
        return None, "ERROR: empty input — required header row `rater,unit,value` not found."
    return rows, None


def units_from_rows(rows):
    """Return (ordered list of units, {unit: [present values]}, set of raters).

    Units are kept in first-seen order for deterministic bootstrap indexing. Missing values (None)
    are dropped from a unit's value list.
    """
    order = []
    by_unit = {}
    raters = set()
    for rater, unit, value in rows:
        raters.add(rater)
        if unit not in by_unit:
            by_unit[unit] = []
            order.append(unit)
        if value is not None:
            by_unit[unit].append(value)
    return order, by_unit, raters


# --------------------------------------------------------------------------
# Krippendorff's alpha over a list of unit value-lists
# --------------------------------------------------------------------------

def _coincidence(unit_values):
    """Build the coincidence matrix from a list of per-unit value-lists.

    Returns (o, marginals, n) where o[c][k] is the (float) coincidence count, marginals[c] is the
    row/column total n_c, and n is the grand total of pairable values. Units with < 2 present
    values contribute nothing.
    """
    o = {}
    for vals in unit_values:
        m = len(vals)
        if m < 2:
            continue
        w = 1.0 / (m - 1)
        for i in range(m):
            ci = vals[i]
            row = o.setdefault(ci, {})
            for j in range(m):
                if i == j:
                    continue
                kj = vals[j]
                row[kj] = row.get(kj, 0.0) + w
    marginals = {}
    for c, row in o.items():
        marginals[c] = sum(row.values())
    n = sum(marginals.values())
    return o, marginals, n


def _nominal_delta2(c, k):
    return 0.0 if c == k else 1.0


def _ordinal_delta2_factory(marginals):
    """Return an ordinal delta2(c,k) closure using Krippendorff's ordinal metric.

    delta2(c,k) = ( sum_{g in [lo..hi]} n_g - (n_lo + n_hi)/2 )^2 over value classes sorted
    numerically, lo/hi the sorted endpoints of {c,k}, inclusive.
    """
    classes = sorted(marginals, key=lambda v: float(v))
    idx = {cl: i for i, cl in enumerate(classes)}
    nsorted = [marginals[cl] for cl in classes]
    # prefix[i] = sum of nsorted[0:i]; inclusive [lo..hi] = prefix[hi+1] - prefix[lo]
    prefix = [0.0]
    for v in nsorted:
        prefix.append(prefix[-1] + v)

    def delta2(c, k):
        i, j = idx[c], idx[k]
        lo, hi = (i, j) if i <= j else (j, i)
        between = prefix[hi + 1] - prefix[lo]
        return (between - (nsorted[lo] + nsorted[hi]) / 2.0) ** 2

    return delta2


def alpha_from_unit_values(unit_values, metric):
    """Compute Krippendorff's alpha. Returns (alpha_or_None, n, Do, De).

    alpha is None when De == 0 (the D_e=0 degenerate case — a single value class). Assumes ordinal
    inputs are already numeric (see _coerce_for_metric)."""
    o, marginals, n = _coincidence(unit_values)
    if n == 0:
        return None, 0.0, 0.0, 0.0
    if metric == "ordinal":
        delta2 = _ordinal_delta2_factory(marginals)
    else:
        delta2 = _nominal_delta2

    classes = list(marginals.keys())
    do = 0.0
    for c in classes:
        row = o.get(c, {})
        for k in classes:
            ock = row.get(k, 0.0)
            if ock:
                do += ock * delta2(c, k)
    de = 0.0
    for c in classes:
        nc = marginals[c]
        for k in classes:
            de += nc * marginals[k] * delta2(c, k)
    if n > 1:
        de /= (n - 1.0)
    else:
        de = 0.0
    if de == 0.0:
        return None, n, do, de
    return 1.0 - do / de, n, do, de


def _coerce_for_metric(by_unit, order, metric):
    """Return a list of per-unit value-lists coerced for the metric.

    nominal: values stay as strings. ordinal: every present value must parse as a FINITE float
    (numeric ordering); a non-numeric or non-finite token raises ValueError naming the offender —
    two `nan` tokens would otherwise become two DISTINCT value classes (nan != nan), silently
    shifting alpha, and `inf` has no defensible rank position.
    """
    out = []
    if metric == "ordinal":
        for u in order:
            vals = []
            for v in by_unit[u]:
                try:
                    f = float(v)
                except (TypeError, ValueError):
                    raise ValueError("ordinal metric requires numeric values; got non-numeric "
                                     "%r in unit %r" % (v, u))
                if not math.isfinite(f):
                    raise ValueError("ordinal metric requires FINITE numeric values; got %r "
                                     "in unit %r (nan/inf have no defensible rank)." % (v, u))
                vals.append(f)
            out.append(vals)
    else:
        for u in order:
            out.append(list(by_unit[u]))
    return out


# --------------------------------------------------------------------------
# Bootstrap CI over UNITS (Hayes & Krippendorff 2007)
# --------------------------------------------------------------------------

def _percentile(sorted_vals, q):
    """Linear-interpolation percentile (numpy 'type 7'). q in [0,100]. sorted_vals nonempty."""
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    rank = (q / 100.0) * (len(sorted_vals) - 1)
    lo = int(rank)
    frac = rank - lo
    if lo + 1 >= len(sorted_vals):
        return sorted_vals[-1]
    return sorted_vals[lo] + frac * (sorted_vals[lo + 1] - sorted_vals[lo])


def bootstrap_ci(unit_values, metric, seed, resamples):
    """Percentile 95% CI by resampling UNITS with replacement.

    Returns (lo, hi, n_defined). Resamples that yield an undefined alpha (D_e=0) are dropped from
    the CI distribution; (None, None, count) if fewer than 2 defined resamples.
    """
    rng = random.Random(seed)
    n_units = len(unit_values)
    defined = []
    for _ in range(resamples):
        sample = [unit_values[rng.randrange(n_units)] for _ in range(n_units)]
        a, _n, _do, _de = alpha_from_unit_values(sample, metric)
        if a is not None:
            defined.append(a)
    if len(defined) < 2:
        return None, None, len(defined)
    defined.sort()
    return _percentile(defined, 2.5), _percentile(defined, 97.5), len(defined)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

_USAGE = ("Usage: agreement_alpha.py agreement-alpha <ratings.csv> "
          "[--metric nominal|ordinal] [--seed <int>] [--resamples <int>=1000] | --self-test")


def _fmt(x):
    return "%.4f" % x


def _run_alpha(args):
    metric = "nominal"
    seed = _DEFAULT_SEED
    resamples = _DEFAULT_RESAMPLES
    path = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--metric" and i + 1 < len(args):
            metric = args[i + 1]; i += 2; continue
        if a == "--seed" and i + 1 < len(args):
            try:
                seed = int(args[i + 1])
            except ValueError:
                sys.stderr.write("ERROR: --seed must be an integer.\n"); return 2
            i += 2; continue
        if a == "--resamples" and i + 1 < len(args):
            try:
                resamples = int(args[i + 1])
            except ValueError:
                sys.stderr.write("ERROR: --resamples must be an integer.\n"); return 2
            i += 2; continue
        if a.startswith("--"):
            sys.stderr.write("ERROR: unknown or incomplete option %r.\n%s\n" % (a, _USAGE)); return 2
        if path is None:
            path = a; i += 1; continue
        sys.stderr.write("ERROR: unexpected extra argument %r.\n%s\n" % (a, _USAGE)); return 2

    if path is None:
        sys.stderr.write(_USAGE + "\n"); return 2
    if metric not in _METRICS:
        sys.stderr.write("ERROR: --metric must be one of %s (got %r).\n"
                         % ("/".join(_METRICS), metric)); return 2
    if resamples < _DEFAULT_RESAMPLES:
        sys.stderr.write("ERROR: --resamples may only RAISE the pinned floor of %d "
                         "(Hayes & Krippendorff 2007 unit-level bootstrap); got %d.\n"
                         % (_DEFAULT_RESAMPLES, resamples)); return 2
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        sys.stderr.write("ERROR: cannot read %s: %s\n" % (path, exc)); return 2

    return _compute_and_emit(text, metric, seed, resamples)


def _compute_and_emit(text, metric, seed, resamples):
    rows, err = read_ratings(text)
    if err is not None:
        print(err)
        print("")
        print("FAILED: ratings CSV did not satisfy the `rater,unit,value` contract.")
        return 1
    order, by_unit, raters = units_from_rows(rows)
    n_raters = len(raters)
    n_units = len(order)
    if n_raters < 2:
        print("ERROR: need >= 2 raters to compute agreement (got %d)." % n_raters)
        print("")
        print("FAILED: insufficient raters.")
        return 2
    if n_units < 2:
        print("ERROR: need >= 2 units to compute agreement (got %d)." % n_units)
        print("")
        print("FAILED: insufficient units.")
        return 2
    try:
        unit_values = _coerce_for_metric(by_unit, order, metric)
    except ValueError as exc:
        print("ERROR: %s" % exc)
        print("")
        print("FAILED: ordinal metric requires numeric values.")
        return 1

    alpha, n, do, de = alpha_from_unit_values(unit_values, metric)
    n_pairable = sum(1 for v in unit_values if len(v) >= 2)
    if n_pairable < 1:
        print("ERROR: no unit has >= 2 ratings — nothing is pairable, alpha is undefined.")
        print("")
        print("FAILED: no pairable units.")
        return 2

    head = ("metric=%s  n_raters=%d  n_units=%d  n_pairable_values=%d  seed=%d  resamples=%d"
            % (metric, n_raters, n_units, int(round(n)), seed, resamples))
    if alpha is None:
        print("alpha=UNDEFINED (D_e=0)  " + head)
        print("WARN: expected disagreement De=0 — a single value class occurs (every rating is "
              "identical), so alpha is 0/0. This does NOT clear any licensing threshold; a "
              "constant column is no evidence of discriminative agreement.")
        return 0

    lo, hi, n_def = bootstrap_ci(unit_values, metric, seed, resamples)
    if lo is None:
        ci_str = "CI95=UNDEFINED (%d/%d resamples defined)" % (n_def, resamples)
    else:
        ci_str = "CI95=[%s, %s] (%d/%d resamples defined)" % (_fmt(lo), _fmt(hi), n_def, resamples)
    print("alpha=%s  %s  %s" % (_fmt(alpha), head, ci_str))
    # Degenerate-interval guard: at tiny n the bootstrap collapses (zero-width survivorship-only
    # intervals, large undefined-resample fractions) and would otherwise print with the same
    # authoritative OK line as a healthy run. The docstring's small-n caveat must reach the
    # OUTPUT when it actually applies.
    pairable_units = sum(1 for vals in unit_values if len(vals) >= 2)
    if lo is not None and ((hi - lo) == 0.0 or n_def < 0.9 * resamples or pairable_units < 4):
        print("WARN: bootstrap CI is unstable at this n (zero-width interval, <90%% defined "
              "resamples, or <%d pairable units) — treat the interval as unreliable and do not "
              "license from it without more units." % 4)
    # Panel floor: the benchmark contract (docs/argument-benchmark-spec.md §GT schema —
    # "panel-licensed | Promoted by measured >=3-editor agreement") licenses a band only from a
    # panel of at least three editors. Alpha is well-defined for two raters, so it is computed and
    # printed above for information — but a two-rater run, however high its agreement, must not emit
    # a clearing verdict the promotion path could act on. Count PARTICIPATING editors (>=1 non-missing
    # rating); an all-blank column is a listed-but-absent editor, not a rating one, and does not count.
    n_rating_editors = len({r for (r, _u, v) in rows if v is not None})
    if n_rating_editors < _PANEL_FLOOR:
        print("FAILED: panel-licensing requires a >= %d-editor panel "
              "(docs/argument-benchmark-spec.md §GT schema); got %d editor(s) with ratings. The "
              "alpha above is informational only and clears NO licensing threshold — a sub-panel "
              "high-agreement run must not promote. Recruit at least %d independent editors and "
              "re-run." % (_PANEL_FLOOR, n_rating_editors, _PANEL_FLOOR))
        return 2
    print("OK: Krippendorff's alpha computed. License on the CI LOWER BOUND, not the point "
          "estimate (small-n false-promotion guard): >= .800 -> panel-licensed, .667-.800 -> "
          "provisional, < .667 -> low-agreement.")
    return 0


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(_USAGE + "\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test()
    if argv[1] == "agreement-alpha":
        return _run_alpha(argv[2:])
    # Convenience: allow a bare path form too.
    if not argv[1].startswith("-"):
        return _run_alpha(argv[1:])
    sys.stderr.write("Error: unknown command: %s\n%s\n" % (argv[1], _USAGE))
    return 2


# --------------------------------------------------------------------------
# Self-test (hermetic).
#
# NUMERICAL HONESTY — every asserted alpha below is derived BY HAND from the coincidence matrix,
# never trusted from this implementation's own output.
#
# (H1) Tiny nominal example, 2 raters x 4 units:
#      u1:(1,1) u2:(1,2) u3:(2,2) u4:(2,2)
#   Coincidence (each m_u=2 unit adds 1/(2-1)=1 per ordered pair):
#      o_11=2 (u1), o_12=1 & o_21=1 (u2), o_22=4 (u3+u4).  Marginals n_1=3, n_2=5, n=8.
#   Do = sum off-diag o = o_12+o_21 = 2.  De = (1/(n-1)) * (n_1 n_2 + n_2 n_1) = (1/7)*30 = 30/7.
#   alpha = 1 - Do/De = 1 - 2/(30/7) = 1 - 14/30 = 1 - 7/15 = 8/15 = 0.5333.
#
# (H2) Krippendorff's PUBLISHED worked example (nominal), 3 coders x 15 units, missing = *:
#      A: * * * * * 3 4 1 2 1 1 3 3 * 3
#      B: 1 * 2 1 3 3 4 3 * * * * * * *
#      C: * * 2 1 3 4 4 * 2 1 1 3 3 * 4
#   Published coincidence matrix (Krippendorff 2011): marginals n_1=7,n_2=4,n_3=10,n_4=5, n=26;
#   off-diagonal ordered-pair total = 6 (o_12=o_21=1, o_34=o_43=2). Published nominal alpha=0.691.
#   Hand-check: Do=6, De=(1/25)*2*(n1n2 + n1n3 + n1n4 + n2n3 + n2n4 + n3n4)
#            = (2/25)*243 = 486/25 = 19.44; alpha = 1 - 6/19.44 = 0.6914. Matches the paper's .691.
#
# (H3) Small ordinal example (neighbor disagreements), 2 raters x 5 units, classes 1<2<3:
#      u1:(1,1) u2:(2,2) u3:(3,3) u4:(1,2) u5:(2,3)
#   Marginals n_1=3, n_2=4, n_3=3, n=10.
#   NOMINAL: alpha = 1 - (n-1)*sum_{c<k}o / sum_{c<k} n_c n_k = 1 - 9*2/33 = 1 - 18/33 = 5/11 = 0.4545.
#   ORDINAL: delta2(1,2)=((n1+n2)-(n1+n2)/2)^2=3.5^2=12.25; delta2(2,3)=3.5^2=12.25;
#            delta2(1,3)=(10-(n1+n3)/2)^2=(10-3)^2=49.
#            Do=2*(o_12*12.25 + o_23*12.25)=2*24.5=49.
#            De=(1/9)*2*(n1n2*12.25 + n1n3*49 + n2n3*12.25)=(2/9)*(147+441+147)=(2/9)*735=163.333.
#            alpha = 1 - 49/163.333 = 1 - 0.3 = 0.7000. Ordinal (0.700) > nominal (0.4545): the
#            ordinal metric credits near-neighbor disagreements, as it must.
# --------------------------------------------------------------------------

# (H1) tiny nominal
_H1_UNITS = [["1", "1"], ["1", "2"], ["2", "2"], ["2", "2"]]
_H1_ALPHA = 8.0 / 15.0                        # 0.53333...

# (H2) Krippendorff's published example (as unit value-lists; * omitted)
_H2_UNITS = [
    ["1"],                    # u1  (single value -> unpairable)
    [],                       # u2  (empty)
    ["2", "2"],               # u3
    ["1", "1"],               # u4
    ["3", "3"],               # u5
    ["3", "3", "4"],          # u6  (A=3, B=3, C=4)
    ["4", "4", "4"],          # u7
    ["1", "3"],               # u8  (A=1, B=3)
    ["2", "2"],               # u9  (A=2, C=2)
    ["1", "1"],               # u10 (A=1, C=1)
    ["1", "1"],               # u11 (A=1, C=1)
    ["3", "3"],               # u12 (A=3, C=3)
    ["3", "3"],               # u13 (A=3, C=3)
    [],                       # u14
    ["3", "4"],               # u15 (A=3, C=4)
]
_H2_ALPHA_NOMINAL = 0.691                      # Krippendorff (2011), published value

# (H3) small ordinal
_H3_UNITS = [["1", "1"], ["2", "2"], ["3", "3"], ["1", "2"], ["2", "3"]]
_H3_ALPHA_NOMINAL = 5.0 / 11.0                 # 0.45454...
_H3_ALPHA_ORDINAL = 0.70

# Deterministic-CI arm: locked bounds for the published example, nominal, pinned seed, 1000
# resamples. Regression-locks the bootstrap PATH itself (not just the point estimate). The exact
# bounds are whatever the seeded Mersenne-Twister path produces; two auditors on the same seed
# reproduce them byte-for-byte. (Value filled in from a first run, then held.)
# Locked from the seeded Mersenne-Twister path (seed=20260709, 1000 resamples, published example,
# nominal). CPython's getrandbits-backed integer draws are version-stable, so this is the exact CI
# two auditors reproduce. The wide interval (lower bound 0.2945 << point 0.6914) is the small-n
# instability the tool warns about, made concrete.
_DET_CI_EXPECTED = ("0.2945", "1.0000")


def run_self_test():
    rc = {"v": 0}

    def approx(name, got, want, tol=5e-4):
        ok = got is not None and abs(got - want) <= tol
        print("  %s: %s" % (name, "OK" if ok else "FAIL (got=%r want=%r)" % (got, want)))
        if not ok:
            rc["v"] = 1

    def truth(name, cond, detail=""):
        print("  %s: %s%s" % (name, "OK" if cond else "FAIL", "" if cond else " (%s)" % detail))
        if not cond:
            rc["v"] = 1

    # (H1) tiny hand-worked nominal example
    a, n, do, de = alpha_from_unit_values(_H1_UNITS, "nominal")
    approx("hand_nominal_tiny", a, _H1_ALPHA)

    # (H2) Krippendorff's published nominal example -> .691
    a, n, do, de = alpha_from_unit_values(_H2_UNITS, "nominal")
    approx("krippendorff_published_nominal", a, _H2_ALPHA_NOMINAL, tol=1e-3)
    truth("krippendorff_n_pairable_is_26", abs(n - 26.0) < 1e-9, "n=%r (expected 26)" % n)

    # (H3) ordinal vs nominal divergence on an ordered example
    an, _, _, _ = alpha_from_unit_values(_H3_UNITS, "nominal")
    ao, _, _, _ = alpha_from_unit_values(_H3_UNITS, "ordinal")
    approx("ordinal_example_nominal", an, _H3_ALPHA_NOMINAL)
    approx("ordinal_example_ordinal", ao, _H3_ALPHA_ORDINAL)
    truth("ordinal_gt_nominal", ao is not None and an is not None and ao > an,
          "ordinal=%r should exceed nominal=%r" % (ao, an))

    # Perfect agreement -> alpha = 1.0
    perfect = [["1", "1"], ["2", "2"], ["3", "3"], ["1", "1"]]
    a, _, _, _ = alpha_from_unit_values(perfect, "nominal")
    approx("perfect_agreement", a, 1.0)

    # Systematic disagreement -> alpha < 0. u1:(1,2) u2:(2,1): o_12=o_21=2, n1=n2=2, n=4.
    #   Do=4, De=(1/3)*(n1n2+n2n1)=(1/3)*8=8/3; alpha=1 - 4/(8/3)=1 - 1.5 = -0.5.
    systematic = [["1", "2"], ["2", "1"]]
    a, _, _, _ = alpha_from_unit_values(systematic, "nominal")
    approx("systematic_disagreement_neg", a, -0.5)
    truth("systematic_is_negative", a is not None and a < 0, "alpha=%r" % a)

    # D_e=0 degenerate: a single value class (constant column) -> UNDEFINED.
    constant = [["7", "7"], ["7", "7"], ["7", "7"]]
    a, _, _, de = alpha_from_unit_values(constant, "nominal")
    truth("De0_undefined_alpha", a is None, "alpha=%r (expected None)" % a)
    truth("De0_is_zero", de == 0.0, "De=%r" % de)
    # ... and the CLI reports UNDEFINED + WARN + exit 0.
    csv_const = "rater,unit,value\nA,u1,7\nB,u1,7\nA,u2,7\nB,u2,7\n"
    out, code = _capture(csv_const, "nominal")
    truth("De0_cli_warn", code == 0 and "alpha=UNDEFINED (D_e=0)" in out and "WARN:" in out,
          "code=%d out=%r" % (code, out))

    # Ordinal on non-numeric values -> ERROR (exit 1).
    try:
        _coerce_for_metric({"u1": ["low", "high"]}, ["u1"], "ordinal")
        truth("ordinal_non_numeric_rejected", False, "no ValueError raised")
    except ValueError:
        truth("ordinal_non_numeric_rejected", True)

    # ---- CSV-contract arms (through the CLI path) ----
    # A two-rater run still COMPUTES and prints alpha (informational), but must NOT clear the panel
    # floor — panel-licensing needs a >=3-editor panel (docs/argument-benchmark-spec.md §GT schema).
    # Non-clearing: exit 2, no "OK:" licensing line.
    good = "rater,unit,value\nA,u1,1\nB,u1,1\nA,u2,1\nB,u2,2\nA,u3,2\nB,u3,2\nA,u4,2\nB,u4,2\n"
    out, code = _capture(good, "nominal")
    truth("cli_two_rater_not_licensable",
          code == 2 and out.startswith("alpha=") and "panel" in out.lower() and "OK:" not in out,
          "code=%d out=%r" % (code, out))
    truth("cli_good_matches_hand", ("alpha=%s" % _fmt(_H1_ALPHA)) in out, "out=%r" % out)

    # A >=3-editor panel with a small disagreement CLEARS the floor: alpha prints + the OK license line.
    good3 = ("rater,unit,value\n"
             "A,u1,1\nB,u1,1\nC,u1,1\n"
             "A,u2,2\nB,u2,2\nC,u2,2\n"
             "A,u3,1\nB,u3,1\nC,u3,1\n"
             "A,u4,2\nB,u4,2\nC,u4,1\n"
             "A,u5,1\nB,u5,1\nC,u5,1\n")
    out, code = _capture(good3, "nominal")
    truth("cli_three_rater_licenses", code == 0 and out.startswith("alpha=") and "OK:" in out,
          "code=%d out=%r" % (code, out))

    # PR #194 P1 regression (the reviewer's repro): two raters, 100 units, two planted disagreements
    # -> a very high alpha with a >= .800 CI lower bound. It must NOT license: non-clearing, exit 2.
    _two = ["rater,unit,value"]
    for _i in range(1, 101):
        _cls = "2" if _i <= 50 else "1"                    # both classes present -> De > 0
        _two.append("A,u%d,%s" % (_i, _cls))
        _bcls = ("1" if _cls == "2" else "2") if _i in (10, 60) else _cls
        _two.append("B,u%d,%s" % (_i, _bcls))
    out, code = _capture("\n".join(_two) + "\n", "nominal")
    truth("cli_two_rater_high_agreement_not_licensed",
          code == 2 and out.startswith("alpha=") and "panel" in out.lower() and "OK:" not in out,
          "code=%d out=%r" % (code, out))

    # PR #194 P1 regression: an editor listed with only BLANK ratings is not a participating editor,
    # so 2 real + 1 all-blank editor is a 2-editor panel and must not license (non-missing count only).
    out, code = _capture(
        "rater,unit,value\n"
        "A,u1,1\nB,u1,1\nC,u1,\n"
        "A,u2,2\nB,u2,2\nC,u2,\n"
        "A,u3,1\nB,u3,1\nC,u3,\n"
        "A,u4,2\nB,u4,2\nC,u4,\n", "nominal")
    truth("cli_all_blank_editor_not_counted",
          code == 2 and out.startswith("alpha=") and "panel" in out.lower() and "OK:" not in out,
          "code=%d out=%r" % (code, out))

    # Missing header -> ERROR.
    out, code = _capture("A,u1,1\nB,u1,1\n", "nominal")
    truth("cli_missing_header", code == 1 and "ERROR:" in out and "header" in out.lower(),
          "code=%d out=%r" % (code, out))

    # Wrong header -> ERROR.
    out, code = _capture("coder,item,val\nA,u1,1\n", "nominal")
    truth("cli_wrong_header", code == 1 and "ERROR:" in out, "code=%d out=%r" % (code, out))

    # Malformed row (2 cols) -> ERROR naming the line number.
    out, code = _capture("rater,unit,value\nA,u1,1\nB,u1\n", "nominal")
    truth("cli_malformed_row", code == 1 and "ERROR:" in out and "line 3" in out,
          "code=%d out=%r" % (code, out))

    # Empty rater/unit -> ERROR.
    out, code = _capture("rater,unit,value\nA,u1,1\n,u1,2\n", "nominal")
    truth("cli_empty_rater", code == 1 and "ERROR:" in out and "line 3" in out,
          "code=%d out=%r" % (code, out))

    # Single rater -> ERROR (usage, exit 2).
    out, code = _capture("rater,unit,value\nA,u1,1\nA,u2,2\n", "nominal")
    truth("cli_single_rater", code == 2 and "ERROR:" in out and "raters" in out,
          "code=%d out=%r" % (code, out))

    # Single unit -> ERROR (usage, exit 2).
    out, code = _capture("rater,unit,value\nA,u1,1\nB,u1,2\n", "nominal")
    truth("cli_single_unit", code == 2 and "ERROR:" in out and "units" in out,
          "code=%d out=%r" % (code, out))

    # Blank value = missing data (not an error): A's u2 value is blank and drops; alpha still computes
    # from the rest. Three participating editors, so it also clears the panel floor.
    out, code = _capture(
        "rater,unit,value\nA,u1,1\nB,u1,1\nC,u1,1\nA,u2,\nB,u2,2\nC,u2,2\nA,u3,2\nB,u3,2\nC,u3,2\n",
        "nominal")
    truth("cli_blank_value_missing", code == 0 and out.startswith("alpha="),
          "code=%d out=%r" % (code, out))

    # A duplicate (rater, unit) row manufactures pairable self-agreement -> loud ERROR
    # (licensing-input hardening; the most plausible panel data-entry accident).
    out, code = _capture("rater,unit,value\nA,u1,1\nA,u1,1\nB,u2,2\nC,u2,2\n", "nominal")
    truth("cli_duplicate_rater_unit", code == 1 and "ERROR:" in out and "duplicate" in out,
          "code=%d out=%r" % (code, out))
    # A repeated header row mid-file (two CSVs concatenated) -> loud ERROR, not a phantom
    # rater named "rater".
    out, code = _capture("rater,unit,value\nA,u1,1\nB,u1,1\nrater,unit,value\nA,u2,2\n",
                         "nominal")
    truth("cli_repeated_header", code == 1 and "ERROR:" in out and "repeated header" in out,
          "code=%d out=%r" % (code, out))
    # Non-finite ordinal values -> loud ERROR (two `nan` tokens must not become two DISTINCT
    # value classes; `inf` has no defensible rank).
    out, code = _capture("rater,unit,value\nA,u1,nan\nB,u1,nan\nA,u2,1\nB,u2,1\n", "ordinal")
    truth("cli_ordinal_nan_rejected", code == 1 and "ERROR:" in out and "FINITE" in out,
          "code=%d out=%r" % (code, out))
    out, code = _capture("rater,unit,value\nA,u1,inf\nB,u1,inf\nA,u2,1\nB,u2,1\n", "ordinal")
    truth("cli_ordinal_inf_rejected", code == 1 and "ERROR:" in out and "FINITE" in out,
          "code=%d out=%r" % (code, out))
    # A degenerate tiny-n CI (zero-width / survivorship-only / <4 pairable units) must carry the
    # instability WARN, not just the authoritative OK line. Three editors so the panel floor clears.
    out, code = _capture("rater,unit,value\nA,u1,1\nB,u1,1\nC,u1,1\nA,u2,2\nB,u2,2\nC,u2,2\n",
                         "nominal")
    truth("cli_tiny_n_ci_warned", code == 0 and "WARN:" in out and "unstable" in out,
          "code=%d out=%r" % (code, out))

    # Bootstrap contract: >= 1000 default; --resamples may only raise.
    truth("bootstrap_floor_is_1000", _DEFAULT_RESAMPLES == 1000)
    rc_low = _run_alpha_capture(["/dev/null-not-read", "--resamples", "500"])
    truth("bootstrap_reject_below_floor", rc_low == 2, "rc=%r" % rc_low)

    # Deterministic CI arm: fixed seed + fixed input -> exact locked bounds; reproducible.
    lo1, hi1, nd1 = bootstrap_ci(_H2_UNITS, "nominal", _DEFAULT_SEED, 1000)
    lo2, hi2, nd2 = bootstrap_ci(_H2_UNITS, "nominal", _DEFAULT_SEED, 1000)
    truth("ci_reproducible", (lo1, hi1, nd1) == (lo2, hi2, nd2),
          "run1=%r run2=%r" % ((lo1, hi1, nd1), (lo2, hi2, nd2)))
    if _DET_CI_EXPECTED is not None:
        got = (_fmt(lo1), _fmt(hi1))
        truth("ci_deterministic_locked", got == _DET_CI_EXPECTED,
              "got=%r want=%r" % (got, _DET_CI_EXPECTED))
        truth("ci_lower_below_point", lo1 <= _H2_ALPHA_NOMINAL + 1e-9,
              "lo=%r point=%r" % (lo1, _H2_ALPHA_NOMINAL))

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def _capture(csv_text, metric):
    """Run _compute_and_emit capturing stdout; return (stdout, exit_code)."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        code = _compute_and_emit(csv_text, metric, _DEFAULT_SEED, _DEFAULT_RESAMPLES)
    finally:
        sys.stdout = old
    return buf.getvalue(), code


def _run_alpha_capture(args):
    """Run _run_alpha capturing stderr/stdout; return exit_code only."""
    old_o, old_e = sys.stdout, sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        return _run_alpha(args)
    finally:
        sys.stdout, sys.stderr = old_o, old_e


if __name__ == "__main__":
    sys.exit(main(sys.argv))
