#!/usr/bin/env bash
#
# run.sh — blind Dialectical Clarity runs for the argument-engine benchmark.
#
# Implements RUN-PROTOCOL.md Steps 1–2 for the referenced real corpus:
#   - PREPARER role: extracts each fixture's argument text from the local cache
#     (per SOURCES.md), strips the provenance header, and (best-effort) checks
#     the recorded SHA-256.
#   - BLIND RUNNER role: inlines the audit reference + the extracted text into a
#     single prompt fed on STDIN, and runs it under two model configs
#     (opus + sonnet) = two independent runs for convergence.
#
# Blindness guarantee: the argument text and audit reference are the ONLY things
# in the prompt. groundtruth.md is never read here. Scoring is a SEPARATE step
# (a fresh session with repo access, or hand the outputs to a scorer) — never
# this script. See RUN-PROTOCOL.md §Step 3–4.
#
# Cached full texts live OUTSIDE the git tree (copyright); this script reads
# them from $SRC and writes model outputs to the gitignored evals/results/.
#
# ---------------------------------------------------------------------------
# USAGE
#   ./run.sh                 # run all fixtures with a recorded hash in SOURCES.md
#   ./run.sh ppi-one-size-fits-none roosevelt-democratic-abundance   # a subset
#   ./run.sh --verify        # only check the cache against recorded hashes
#
# REQUIRED: point these at your machine (env-overridable, no edit needed):
#   SRC   — dir holding the cached <slug>.md / <slug>-corrected.md texts
#   REPO  — the apodictic clone (defaults to this script's repo)
#
# TUNABLE (only if your CLI/cache differ from the defaults):
#   CLAUDE_BIN         claude binary           (default: claude)
#   MODELS             space-separated configs (default: "opus sonnet")
#   CLAUDE_TOOL_FLAGS  extra flags to harden blindness by disabling tools.
#                      Default empty — blindness already holds because the text
#                      is fully inlined and nothing instructs the model to read
#                      files. To harden, set e.g.:
#                        CLAUDE_TOOL_FLAGS='--allowedTools '         (older CLI)
#                        CLAUDE_TOOL_FLAGS='--allowed-tools ""'      (newer CLI)
#                      Confirm your CLI's exact flag with `claude --help`.
#   STRIP_CMD          custom header-stripper, reads file on STDIN, writes the
#                      argument body to STDOUT. Default heuristic: drop everything
#                      up to and including the first `---` line in the first 25
#                      lines (covers YAML/`---`-delimited provenance headers).
#   REQUIRE_HASH       1 = refuse to run a fixture whose text fails hash check;
#                      0 = warn and run anyway (default — see note below).
#
# NOTE on hashing: SOURCES.md records the SHA-256 of the cached text. This check
# is BEST-EFFORT: it compares both the whole file and the runner-visible body
# (the slug's BODY_START/BODY_END-anchored body, exactly what the runner sends)
# to the recorded hash and reports which (if either) matches. A mismatch does not
# affect run validity (blindness is structural, not hash-dependent); it only
# flags that reproducibility provenance needs reconciling. Set REQUIRE_HASH=1 to
# be strict.
# ---------------------------------------------------------------------------

set -uo pipefail

# --- locate repo + inputs -------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${REPO:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
SRC="${SRC:-$HOME/Library/CloudStorage/Dropbox/Cowork/Development Editor/argument-benchmark-sources}"
AUDIT="$REPO/plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md"
SOURCES="$SCRIPT_DIR/SOURCES.md"

CLAUDE_BIN="${CLAUDE_BIN:-claude}"
MODELS="${MODELS:-opus sonnet}"
CLAUDE_TOOL_FLAGS="${CLAUDE_TOOL_FLAGS:-}"
REQUIRE_HASH="${REQUIRE_HASH:-0}"

OUT="$REPO/evals/results/run-$(date +%Y%m%d-%H%M%S)"

die() { echo "ERROR: $*" >&2; exit 1; }
[ -f "$AUDIT" ]   || die "audit reference not found: $AUDIT"
[ -f "$SOURCES" ] || die "SOURCES.md not found: $SOURCES"
# --fetch may bootstrap a fresh cache; --verify and model-run modes require it to exist.
[ "${1:-}" = "--fetch" ] && mkdir -p "$SRC" 2>/dev/null
[ -d "$SRC" ]     || die "source cache dir not found: $SRC  (set SRC=...)"

# --- parse slug -> recorded sha256 from SOURCES.md ------------------------
# Each block: a `### <slug>` heading, then a `- **RECORDED:** ...sha256: <hex>`.
parse_hashes() {
  awk '
    /^### /            { slug=$2; next }
    /sha256: [0-9a-f]/ {
      line=$0; sub(/.*sha256: /,"",line); sub(/[^0-9a-f].*/,"",line)
      if (slug != "" && length(line)==64) { print slug "\t" line; slug="" }
    }
  ' "$SOURCES"
}

# --- locate the cached file for a slug (prefer the -corrected copy) -------
src_file() {
  local s="$1"
  if   [ -f "$SRC/$s-corrected.md" ];  then echo "$SRC/$s-corrected.md"
  elif [ -f "$SRC/$s-corrected.txt" ]; then echo "$SRC/$s-corrected.txt"
  elif [ -f "$SRC/$s.md" ];            then echo "$SRC/$s.md"
  elif [ -f "$SRC/$s.txt" ];           then echo "$SRC/$s.txt"
  else return 1; fi
}

# --- read a literal anchor (BODY_START / BODY_END) for a slug from SOURCES.md
sources_anchor() {           # $1 = slug, $2 = field label (BODY_START | BODY_END)
  awk -v slug="$1" -v field="$2" '
    $0=="### " slug {inblk=1; next}
    /^### / {inblk=0}
    inblk && index($0,"**" field ":**")>0 {
      i=index($0,"`"); rest=substr($0,i+1); j=index(rest,"`")
      if (i>0 && j>0) { print substr(rest,1,j-1); exit }
    }
  ' "$SOURCES"
}

# --- read the retrieval URL for a slug from SOURCES.md (for --fetch) -------
sources_url() {              # $1 = slug; prefers SOURCE_PDF, else any **URL...:** field
  awk -v slug="$1" '
    $0=="### " slug {inblk=1; next}
    /^### / {inblk=0}
    inblk && index($0,"**SOURCE_PDF")>0 {
      line=$0; sub(/.*\*\*SOURCE_PDF[^:]*:\*\*[[:space:]]*/,"",line); sub(/[[:space:]].*/,"",line); pdf=line
    }
    inblk && index($0,"**URL")>0 && url=="" {
      line=$0; sub(/.*\*\*URL[^:]*:\*\*[[:space:]]*/,"",line); sub(/[[:space:]].*/,"",line); url=line
    }
    END { if (pdf!="") print pdf; else print url }
  ' "$SOURCES"
}

# --- strip the provenance header AND article masthead to get the argument body
# Removes three layers of identifying metadata so the blind runner sees only the
# argument prose: (1) the `---`-fenced provenance header (SLUG/SOURCE_URL/...),
# stripped through its CLOSING fence (a prior bug stripped only the opening
# `---`, leaking the slug + source URL into the run); (2) the article masthead
# (title/deck/byline/date), cut at the literal BODY_START anchor; (3) the trailing
# author bio / "about" / recommended-citation footer, cut at the BODY_END anchor.
# Both anchors live per slug in SOURCES.md. A custom STRIP_CMD overrides all.
extract_body() {
  local f="$1" slug="${2:-}"
  if [ -n "${STRIP_CMD:-}" ]; then bash -c "$STRIP_CMD" < "$f"; return; fi
  local body=""
  if head -1 "$f" | grep -qE '^---[[:space:]]*$'; then
    local close; close="$(head -40 "$f" | grep -nE '^---[[:space:]]*$' | sed -n '2p' | cut -d: -f1)"
    [ -n "$close" ] && body="$(sed "1,${close}d" "$f")"
  fi
  [ -n "$body" ] || body="$(cat "$f")"
  if [ -n "$slug" ]; then
    # Drop the leading article masthead (title/byline/date) at BODY_START.
    local anchor; anchor="$(sources_anchor "$slug" BODY_START)"
    if [ -n "$anchor" ]; then
      local ln; ln="$(printf '%s\n' "$body" | grep -nF -- "$anchor" | head -1 | cut -d: -f1)"
      [ -n "$ln" ] && [ "$ln" -gt 1 ] && body="$(printf '%s\n' "$body" | sed "1,$((ln-1))d")"
    fi
    # Drop the trailing author bio / "about" / citation footer at BODY_END.
    local eanchor; eanchor="$(sources_anchor "$slug" BODY_END)"
    if [ -n "$eanchor" ]; then
      local eln; eln="$(printf '%s\n' "$body" | grep -nF -- "$eanchor" | head -1 | cut -d: -f1)"
      [ -n "$eln" ] && [ "$eln" -gt 1 ] && body="$(printf '%s\n' "$body" | sed "${eln},\$d")"
    fi
  fi
  printf '%s\n' "$body"
}

# SHA-256 tool: macOS ships `shasum`, most Linux/WSL ship `sha256sum`. Prefer
# whichever exists so the hash check works on macOS, Linux, and Git Bash/WSL.
if command -v shasum >/dev/null 2>&1; then
  sha() { shasum -a 256 | awk '{print $1}'; }
elif command -v sha256sum >/dev/null 2>&1; then
  sha() { sha256sum | awk '{print $1}'; }
else
  die "no SHA-256 tool found (need shasum or sha256sum)"
fi

# --- best-effort hash check; echoes "whole|body|none" ---------------------
hash_status() {
  local f="$1" want="$2" slug="${3:-}"
  [ "$(sha < "$f")" = "$want" ] && { echo whole; return; }
  [ "$(extract_body "$f" "$slug" | sha)" = "$want" ] && { echo body; return; }
  echo none
}

# --- the blind-run prompt header (instructions only; no answer key) -------
read -r -d '' HEADER <<'EOF'
You are running the APODICTIC "Dialectical Clarity" audit on a piece of
argument-shaped nonfiction. Diagnose ONLY from the text inside <submission>.
Produce a structural diagnosis; never rewrite or invent content (the Editor's
Firewall). Apply the audit reference inside <audit_reference>: run all 9 steps;
use its code families (AT, AC, CL, SM, WR, BP, OB, DI, NE) and named patterns
(FM-A1..FM-A20); end with Step 9 (Distinguish: SOUND / UNCONVENTIONAL-BUT-
EFFECTIVE / UNSOUND) and a priority diagnosis (primary structural break, FM-A
pattern(s), severity ranking, first repair target). Do not open any files; the
text is all here. Finish with a line beginning "RECOGNITION:" stating yes/no
whether you recognized the author/title or its standard published critiques,
naming them if yes.
EOF

# --- main -----------------------------------------------------------------
VERIFY_ONLY=0
[ "${1:-}" = "--verify" ] && { VERIFY_ONLY=1; shift; }
FETCH_ONLY=0
[ "${1:-}" = "--fetch" ] && { FETCH_ONLY=1; shift; }

# slug -> recorded sha256, kept as TAB-separated lines. Bash 3.2 compatible:
# macOS ships bash 3.2, which lacks `declare -A`, and the blind runs happen on
# the Mac, so the runner must not depend on associative arrays.
PAIRS="$(parse_hashes)"
[ -n "$PAIRS" ] || die "no recorded hashes parsed from SOURCES.md"
want_for() { printf '%s\n' "$PAIRS" | awk -F'\t' -v s="$1" '$1==s{print $2; exit}'; }

# fixtures to process: CLI args, else all parsed slugs
if [ "$#" -gt 0 ]; then SLUGS=("$@"); else SLUGS=($(printf '%s\n' "$PAIRS" | awk -F'\t' '{print $1}')); fi

# --- --fetch: reconstitute referenced texts from their pinned URLs ----------
# Fetches each slug's source from its SOURCES.md URL, carves the analyzed body
# by the same anchors a run uses, writes it to $SRC/<slug>.md, and verifies the
# recorded SHA-256. This is the "ship a fetch-list, reconstitute locally" path:
# copyrighted/public-domain text is never stored in the repo, only fetched here.
# PDF sources (URL ends in .pdf, e.g. SOURCE_PDF fixtures) reconstitute only when
# `pdftotext` (poppler) is installed; without it the PDF fixture fails loudly with
# a manual path (blindness/hash discipline is identical — see the loop below).
if [ "$FETCH_ONLY" -eq 1 ]; then
  command -v curl >/dev/null 2>&1 || die "curl not found (needed for --fetch)"
  echo "mode=fetch"; echo "src=$SRC"; echo
  ffail=0
  for s in "${SLUGS[@]}"; do
    url="$(sources_url "$s")"
    want="$(want_for "$s")"
    if [ -z "$url" ]; then
      # A recorded-hash source with no fetchable URL is a real failure, not a skip.
      if [ -n "$want" ]; then echo "FAIL  $s  (recorded-hash source, but no fetchable URL parsed from SOURCES.md)"; ffail=1
      else echo "SKIP  $s  (no URL in SOURCES.md — stored/manual fixture)"; fi
      continue
    fi
    # PDF sources need a text-extraction step before the shared anchor/hash tail.
    # If `pdftotext` (poppler) is present, fetch → convert → carve by the same
    # anchors as an HTML fetch; otherwise keep the loud manual path, naming the
    # `pdftotext` option so the operator knows the one dependency that unblocks it.
    is_pdf=0
    case "$url" in *.pdf|*.PDF) is_pdf=1;; esac
    if [ "$is_pdf" -eq 1 ] && ! command -v pdftotext >/dev/null 2>&1; then
      echo "FAIL  $s  (analyzed text is a PDF: $url — --fetch's plain-text pipeline needs \`pdftotext\` (poppler) to reconstitute it; install it (brew install poppler / apt-get install poppler-utils) and re-run, or fetch + convert and place the body at \$SRC/$s.md manually)"; ffail=1; continue
    fi
    tmp="$(mktemp)"
    if ! curl -fsSL --max-time 90 "$url" -o "$tmp"; then echo "FAIL  $s  (fetch error: $url)"; rm -f "$tmp"; ffail=1; continue; fi
    if [ "$is_pdf" -eq 1 ]; then
      txt="$(mktemp)"
      # -layout keeps reading order closest to the visible page; -q silences poppler notices.
      if ! pdftotext -layout -q "$tmp" "$txt"; then echo "FAIL  $s  (pdftotext conversion failed: $url)"; rm -f "$tmp" "$txt"; ffail=1; continue; fi
      rm -f "$tmp"; tmp="$txt"
    fi
    body="$(extract_body "$tmp" "$s")"; rm -f "$tmp"
    [ -n "$body" ] || { echo "FAIL  $s  (empty after extract — check anchors)"; ffail=1; continue; }
    dest="$SRC/$s.md"; printf '%s\n' "$body" > "$dest"
    got="$(sha < "$dest")"
    if   [ -z "$want" ];          then echo "GOT   $s  (sha256: $got; no recorded hash to check) -> ${dest#$SRC/}"
    elif [ "$got" = "$want" ];    then echo "OK    $s  (hash matches recorded) -> ${dest#$SRC/}"
    else echo "HASH? $s  (got $got != recorded $want — reconcile anchors/source)"; ffail=1; fi
  done
  echo; echo "Fetch complete. Texts in: $SRC"
  exit $ffail
fi

[ "$VERIFY_ONLY" -eq 1 ] || mkdir -p "$OUT"
echo "repo=$REPO"
echo "src=$SRC"
[ "$VERIFY_ONLY" -eq 1 ] && echo "mode=verify-only" || echo "out=$OUT"
echo

fail=0
for s in "${SLUGS[@]}"; do
  want="$(want_for "$s")"
  [ -n "$want" ] || { echo "SKIP  $s  (no recorded hash in SOURCES.md)"; continue; }
  f="$(src_file "$s")" || { echo "MISS  $s  (no cached file in \$SRC)"; fail=1; continue; }

  st="$(hash_status "$f" "$want" "$s")"
  case "$st" in
    whole) echo "OK    $s  (hash: whole-file)";;
    body)  echo "OK    $s  (hash: runner-visible body)";;
    none)  echo "HASH? $s  (recorded hash matched neither whole nor stripped — provenance needs reconciling)";;
  esac

  [ "$VERIFY_ONLY" -eq 1 ] && continue
  if [ "$st" = none ] && [ "$REQUIRE_HASH" = 1 ]; then
    echo "      -> skipped (REQUIRE_HASH=1)"; fail=1; continue
  fi

  body="$(extract_body "$f" "$s")"
  [ -n "$body" ] || { echo "      -> empty after strip; skipping"; fail=1; continue; }
  prompt="$(printf '%s\n\n<audit_reference>\n%s\n</audit_reference>\n\n<submission label="Submission X">\n%s\n</submission>\n' \
            "$HEADER" "$(cat "$AUDIT")" "$body")"

  for m in $MODELS; do
    dest="$OUT/${s}__${m}.md"
    echo "      run [$m] -> ${dest#$REPO/}"
    if printf '%s' "$prompt" | "$CLAUDE_BIN" -p --model "$m" $CLAUDE_TOOL_FLAGS > "$dest" 2>"$dest.err"; then
      rm -f "$dest.err"
    else
      echo "      ! $m failed (see $dest.err)"; fail=1
    fi
  done
done

echo
if [ "$VERIFY_ONLY" -eq 1 ]; then
  echo "Verify complete."
else
  echo "Runs complete. Outputs in: $OUT"
  echo "Next: score each *__<model>.md against its groundtruth.md per RUN-PROTOCOL.md §Step 3-4"
  echo "      (a separate session WITH repo access — or send the outputs to a scorer)."
fi
exit $fail
