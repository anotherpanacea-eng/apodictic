#!/usr/bin/env bash
#
# run.sh — blind Core-DE structural runs for the fiction benchmark.
#
# Forked from evals/fixtures/argument-benchmark/run.sh (the shippable-kit model).
# The fork is deliberate (blast-radius-safe: the shipped argument kit is
# untouched); an --engine generalization is a clean Increment-2 refactor once two
# runners exist to factor from.
#
# Implements RUN-PROTOCOL.md Steps 1–2 for the fiction slice:
#   - PREPARER role: already pinned the ten committed short fixtures and their
#     hashes. At runtime, --fetch reconstitutes referenced Gutenberg bodies
#     (required for Dickens), and strict verification checks every selected
#     input against SOURCES.md.
#   - BLIND RUNNER role: inlines the fiction text into a single prompt fed on
#     STDIN, and runs it under two cross-vendor configs (Terra + Opus) = two
#     independent runs for convergence.
#
# Blindness guarantee: the fiction text is the ONLY thing in the prompt.
# groundtruth.md is never read here. The pinned canonical pass-set {0,1,2,5,7,8,10}
# + Synthesis is byte-identical across ALL fixtures, so the pass selection leaks
# zero information about which defect (if any) a fixture carries. Scoring is a
# SEPARATE step (a fresh session with repo access, or hand the outputs to a
# scorer) — never this script. See RUN-PROTOCOL.md §Step 3–4.
#
# Short pinned texts live in-repo; the referenced Dickens text lives in $SRC.
# Model outputs go to the gitignored evals/results/.
#
# ---------------------------------------------------------------------------
# USAGE
#   ./run.sh                 # run all fixtures with a recorded hash in SOURCES.md
#   ./run.sh pov-break-broken orphan-scene-clean   # a subset (by slug)
#   ./run.sh --verify        # only check the cache against recorded hashes
#   ./run.sh --fetch         # reconstitute referenced PD texts from pinned URLs
#   ./run.sh --prompt-only   # verify hashes and materialize blind prompts only
#
# REQUIRED: point these at your machine (env-overridable, no edit needed):
#   SRC   — dir holding the cached / derived <slug>.md texts
#   REPO  — the apodictic clone (defaults to this script's repo)
#
# TUNABLE (only if your CLI/cache differ from the defaults):
#   CONFIGS            space-separated configs (default: "terra opus")
#   CODEX_BIN          Codex binary            (default: codex)
#   TERRA_MODEL        Codex Terra model slug  (default: gpt-5.6-terra)
#   TERRA_EFFORT       Terra reasoning effort  (default: high)
#   CLAUDE_BIN         Claude binary           (default: claude)
#   OPUS_MODEL         concrete Claude model   (default: claude-opus-4-8)
#   RUN_CWD            optional neutral working directory override. By default,
#                      each actual run creates a fresh directory under TMPDIR.
#   STRIP_CMD          custom header-stripper, reads file on STDIN, writes the
#                      fiction body to STDOUT. Default heuristic: drop everything
#                      up to and including the second `---` line (a `---`-fenced
#                      provenance header), then carve at BODY_START/BODY_END.
#   REQUIRE_HASH       1 = refuse to run a fixture whose text fails hash check
#                      (default); 0 = warn and run anyway.
#
# NOTE on hashing: benchmark runs are strict by default. REQUIRE_HASH=0 is a
# troubleshooting escape hatch only and does not produce a valid M2a run.
# macOS ships bash 3.2 (no `declare -A`), so hashes are TAB-separated lines,
# not an associative array — the blind runs happen on the Mac.
# ---------------------------------------------------------------------------

set -uo pipefail

# --- locate repo + inputs -------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${REPO:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
SRC="${SRC:-$HOME/Library/CloudStorage/Dropbox/Cowork/Development Editor/fiction-benchmark-sources}"
SOURCES="$SCRIPT_DIR/SOURCES.md"

CONFIGS="${CONFIGS:-terra opus}"
CODEX_BIN="${CODEX_BIN:-codex}"
TERRA_MODEL="${TERRA_MODEL:-gpt-5.6-terra}"
TERRA_EFFORT="${TERRA_EFFORT:-high}"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"
OPUS_MODEL="${OPUS_MODEL:-claude-opus-4-8}"
REQUIRE_HASH="${REQUIRE_HASH:-1}"
RUN_CWD="${RUN_CWD:-}"
RUN_CWD_OWNED=0

OUT="$REPO/evals/results/fiction-run-$(date +%Y%m%d-%H%M%S)"

die() { echo "ERROR: $*" >&2; exit 1; }
[ -f "$SOURCES" ] || die "SOURCES.md not found: $SOURCES"
# --fetch may bootstrap a fresh cache; other modes can fall back to committed
# short fixtures and report MISS only for a selected external source.
[ "${1:-}" = "--fetch" ] && mkdir -p "$SRC" 2>/dev/null

# --- parse slug -> recorded sha256 from SOURCES.md ------------------------
# Each block: a `### <slug>` heading, then a `- **RECORDED...:** ...sha256: <hex>`.
# A block may carry TWO recorded hashes (a matched pair's clean+broken); each is
# keyed by the slug it names in the label — but the slice keeps each member in
# its OWN block by slug, so one hash per block. A pending/blank hash is skipped.
parse_hashes() {
  awk '
    /^### /            { slug=$2; next }
    /sha256: [0-9a-f]/ {
      line=$0; sub(/.*sha256: /,"",line); sub(/[^0-9a-f].*/,"",line)
      if (slug != "" && length(line)==64) { print slug "\t" line; slug="" }
    }
  ' "$SOURCES"
}

# --- locate the cached file for a slug -------------------------------------
src_file() {
  local s="$1"
  if   [ -f "$SRC/$s.md" ];  then echo "$SRC/$s.md"
  elif [ -f "$SRC/$s.txt" ]; then echo "$SRC/$s.txt"
  elif [ -f "$SCRIPT_DIR/$s/fixture.md" ]; then echo "$SCRIPT_DIR/$s/fixture.md"
  elif [[ "$s" == *-clean ]] && [ -f "$SCRIPT_DIR/${s%-clean}/clean/fixture.md" ]; then echo "$SCRIPT_DIR/${s%-clean}/clean/fixture.md"
  elif [[ "$s" == *-broken ]] && [ -f "$SCRIPT_DIR/${s%-broken}/broken/fixture.md" ]; then echo "$SCRIPT_DIR/${s%-broken}/broken/fixture.md"
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
sources_url() {              # $1 = slug; the first **URL...:** field in the block
  awk -v slug="$1" '
    $0=="### " slug {inblk=1; next}
    /^### / {inblk=0}
    inblk && index($0,"**URL")>0 && url=="" {
      line=$0; sub(/.*\*\*URL[^:]*:\*\*[[:space:]]*/,"",line); sub(/[[:space:]].*/,"",line); url=line
    }
    END { print url }
  ' "$SOURCES"
}

# --- strip a `---`-fenced provenance header, then carve the body at anchors
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
    local anchor; anchor="$(sources_anchor "$slug" BODY_START)"
    if [ -n "$anchor" ]; then
      local ln; ln="$(printf '%s\n' "$body" | grep -nF -- "$anchor" | head -1 | cut -d: -f1)"
      [ -n "$ln" ] && [ "$ln" -gt 1 ] && body="$(printf '%s\n' "$body" | sed "1,$((ln-1))d")"
    fi
    local eanchor; eanchor="$(sources_anchor "$slug" BODY_END)"
    if [ -n "$eanchor" ]; then
      local eln; eln="$(printf '%s\n' "$body" | grep -nF -- "$eanchor" | head -1 | cut -d: -f1)"
      [ -n "$eln" ] && [ "$eln" -gt 1 ] && body="$(printf '%s\n' "$body" | sed "${eln},\$d")"
    fi
  fi
  # Pin logical text, not a transport-specific CRLF/LF representation.
  printf '%s\n' "$body" | tr -d '\r'
}

# SHA-256 tool: macOS `shasum`, Linux/WSL `sha256sum`.
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
# The pinned canonical pass-set is byte-identical across all fixtures (anti-leak).
read -r -d '' HEADER <<'EOF'
You are running the APODICTIC Core Development Editor's structural diagnostic on
a complete short work of fiction. Diagnose ONLY from the text inside
<submission>. Produce a structural diagnosis; never rewrite or invent content,
and never add a scene, character, fact, or quote the text does not contain (the
Editor's Firewall). Treat the submission as a COMPLETE manuscript (not a partial
draft). Run the canonical pass-set — Pass 0 (reverse outline), Pass 1, Pass 2
(beat map / causal chain / orphan scenes), Pass 5 (character cards / agency),
Pass 7 (POV distribution / perspective slips), Pass 8 (reveal timeline / dropped
threads / fairness), Pass 10 (entity + timeline) — and then Synthesis. Emit
material findings as apodictic.finding.v1 blocks with F-<ORIGIN>-<NN> ids,
in-text evidence_refs, a free-text mechanism, and a severity
(Must-Fix/Should-Fix/Could-Fix); continuity/reveal issues may instead (or also)
surface as continuity-bible CF-NN or setup-payoff SP-NN artifact rows. Do not
open any files; the text is all here. Finish with a line beginning
"RECOGNITION:" stating yes/no whether you recognized the author/title, naming it
if yes.
EOF

# --- provider adapters -----------------------------------------------------
# Both adapters receive the exact same prompt bytes from STDIN. They run from a
# neutral directory, ignore user/project instruction sources, and do not persist
# sessions. The pinned HEADER above is the cross-provider Core-DE projection.
run_config() {             # config prompt output stderr
  local config="$1" prompt="$2" output="$3" err="$4"
  case "$config" in
    terra)
      command -v "$CODEX_BIN" >/dev/null 2>&1 || { echo "Codex binary not found: $CODEX_BIN" > "$err"; return 1; }
      (cd "$RUN_CWD" && "$CODEX_BIN" exec \
        --model "$TERRA_MODEL" \
        --ephemeral \
        --ignore-user-config \
        --ignore-rules \
        --sandbox read-only \
        --skip-git-repo-check \
        -c "model_reasoning_effort=\"$TERRA_EFFORT\"" \
        -) < "$prompt" > "$output" 2> "$err"
      ;;
    opus)
      command -v "$CLAUDE_BIN" >/dev/null 2>&1 || { echo "Claude binary not found: $CLAUDE_BIN" > "$err"; return 1; }
      (cd "$RUN_CWD" && "$CLAUDE_BIN" \
        --print \
        --no-session-persistence \
        --permission-mode dontAsk \
        --tools= \
        --setting-sources "" \
        --strict-mcp-config \
        --mcp-config '{"mcpServers":{}}' \
        --model "$OPUS_MODEL") < "$prompt" > "$output" 2> "$err"
      ;;
    *)
      echo "Unknown benchmark config: $config" > "$err"
      return 1
      ;;
  esac
}

# --- main -----------------------------------------------------------------
VERIFY_ONLY=0
[ "${1:-}" = "--verify" ] && { VERIFY_ONLY=1; shift; }
FETCH_ONLY=0
[ "${1:-}" = "--fetch" ] && { FETCH_ONLY=1; shift; }
PROMPT_ONLY=0
[ "${1:-}" = "--prompt-only" ] && { PROMPT_ONLY=1; shift; }

if [ "$VERIFY_ONLY" -eq 0 ] && [ "$FETCH_ONLY" -eq 0 ] && [ "$PROMPT_ONLY" -eq 0 ]; then
  if [ -z "$RUN_CWD" ]; then
    RUN_CWD="$(mktemp -d "${TMPDIR:-/tmp}/apodictic-fiction-benchmark-runner.XXXXXX")" || die "could not create neutral run directory"
    RUN_CWD_OWNED=1
    cleanup_run_cwd() { [ "$RUN_CWD_OWNED" -eq 1 ] && rm -rf "$RUN_CWD"; }
    trap cleanup_run_cwd EXIT
  else
    mkdir -p "$RUN_CWD" || die "could not create RUN_CWD: $RUN_CWD"
  fi
fi

# slug -> recorded sha256, TAB-separated lines (bash 3.2 compatible).
PAIRS="$(parse_hashes)"
want_for() { printf '%s\n' "$PAIRS" | awk -F'\t' -v s="$1" '$1==s{print $2; exit}'; }

# fixtures to process: CLI args, else all parsed slugs
if [ "$#" -gt 0 ]; then
  SLUGS=("$@")
  for s in "${SLUGS[@]}"; do
    [ -n "$(want_for "$s")" ] || die "unknown or unregistered fixture slug: $s"
  done
else
  SLUGS=($(printf '%s\n' "$PAIRS" | awk -F'\t' '{print $1}'))
fi

# --- --fetch: reconstitute referenced PD texts from their pinned URLs -------
# The referenced Carol and the two stored public-domain controls have URLs.
# Synthetic matched-pair members are already committed and have no URL, so
# --fetch skips them; normal run/verify modes read their fixture.md files.
if [ "$FETCH_ONLY" -eq 1 ]; then
  command -v curl >/dev/null 2>&1 || die "curl not found (needed for --fetch)"
  echo "mode=fetch"; echo "src=$SRC"; echo
  ffail=0
  # --fetch iterates the SOURCES.md slugs that carry a URL, not only recorded-hash
  # ones (a fresh clone has blank hashes — fetching is how the hash gets recorded).
  FETCH_SLUGS=($(awk '/^### /{print $2}' "$SOURCES"))
  [ "$#" -gt 0 ] && FETCH_SLUGS=("$@")
  for s in "${FETCH_SLUGS[@]}"; do
    url="$(sources_url "$s")"
    want="$(want_for "$s")"
    if [ -z "$url" ]; then
      echo "SKIP  $s  (no URL in SOURCES.md — committed synthetic fixture)"
      continue
    fi
    tmp="$(mktemp)"
    if ! curl -fsSL --max-time 90 "$url" -o "$tmp"; then echo "FAIL  $s  (fetch error: $url)"; rm -f "$tmp"; ffail=1; continue; fi
    body="$(extract_body "$tmp" "$s")"; rm -f "$tmp"
    [ -n "$body" ] || { echo "FAIL  $s  (empty after extract — check anchors)"; ffail=1; continue; }
    dest="$SRC/$s.md"; printf '%s\n' "$body" > "$dest"
    got="$(sha < "$dest")"
    if   [ -z "$want" ];          then echo "GOT   $s  (sha256: $got; no recorded hash to check) -> ${dest#$SRC/}"
    elif [ "$got" = "$want" ];    then echo "OK    $s  (hash matches recorded) -> ${dest#$SRC/}"
    else echo "HASH? $s  (got $got != recorded $want — reconcile anchors/source)"; ffail=1; fi
  done
  echo; echo "Fetch complete. Texts in: $SRC"
  echo "NOTE: committed synthetic pair members are used directly, not fetched."
  exit $ffail
fi

[ -n "$PAIRS" ] || die "no recorded hashes parsed from SOURCES.md (run ./run.sh --fetch first, or record base hashes at pin time)"

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
  if [ "$st" = "none" ]; then
    if [ "$REQUIRE_HASH" = "1" ]; then echo "HASH  $s  (mismatch; REQUIRE_HASH=1 — skipping)"; fail=1; continue; fi
    echo "WARN  $s  (hash mismatch — running anyway; set REQUIRE_HASH=1 to be strict)"
  fi
  [ "$VERIFY_ONLY" -eq 1 ] && { echo "OK    $s  (hash: $st)"; continue; }

  body="$(extract_body "$f" "$s")"
  [ -n "$body" ] || { echo "FAIL  $s  (empty body after extract)"; fail=1; continue; }

  for m in $CONFIGS; do
    outdir="$OUT/$s"; mkdir -p "$outdir"
    prompt="$outdir/prompt-$m.txt"
    {
      printf '%s\n\n' "$HEADER"
      printf '<submission>\n%s\n</submission>\n' "$body"
    } > "$prompt"
    if [ "$PROMPT_ONLY" -eq 1 ]; then
      echo "PROMPT $s  [$m]  -> ${prompt#$REPO/}"
      continue
    fi
    echo "RUN   $s  [$m]  -> ${outdir#$REPO/}/output-$m.md"
    if ! run_config "$m" "$prompt" "$outdir/output-$m.md" "$outdir/err-$m.txt"; then
      echo "  (model run failed for $s [$m]; see err-$m.txt)"; fail=1
    elif [ ! -s "$outdir/output-$m.md" ]; then
      echo "  (model run returned an empty output for $s [$m])"; fail=1
    elif ! awk 'NF { last=$0 } END { exit(last ~ /^RECOGNITION:/ ? 0 : 1) }' "$outdir/output-$m.md"; then
      echo "  (model output does not end with required RECOGNITION line for $s [$m])"; fail=1
    fi
  done
done

echo
[ "$VERIFY_ONLY" -eq 1 ] && echo "Verify complete." || { [ "$PROMPT_ONLY" -eq 1 ] && echo "Prompt materialization complete. Outputs in: $OUT" || echo "Runs complete. Outputs in: $OUT"; }
echo "Scoring is a SEPARATE step — never this script. See RUN-PROTOCOL.md §Step 3–4."
exit $fail
