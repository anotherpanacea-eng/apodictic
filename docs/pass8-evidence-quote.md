# Pass 8 evidence quotes: conditional producer adoption

**Status:** Built (producer guidance and invented mechanical example, 2026-10-04).

Pass 8 may attach `evidence_quote` only when its finding concerns a complete,
already-cited single-line reveal, signpost or withholding sentence. Keep the
intended `evidence_refs`; omit the quote for structural timing, absent clues or
signposts, dropped threads and cross-line evidence. Do not invent, paraphrase,
concatenate or choose a convenient sentence merely to get a fine anchor.

The existing consumer tries the quote before the refs ladder. A unique quote
from elsewhere therefore wins even when the refs cite another chapter. A6 checks
value, unique occurrence and offsets, not sentence completeness, editorial
relevance or agreement with the intended refs locus. No schema or consumer change
is needed. Pass 5 retains its pilot guidance; other passes remain demand-gated.

## Executable invented worked pair

All manuscript prose and findings below are invented. The judgments serve only
to illustrate producer choices. This checks the existing consumer mechanically;
it does **not** evaluate a model's prompt adherence, fairness diagnosis or editorial
correctness. Run from the repository root using Python 3 (on Windows,
`py -3.12` may replace `python3`). Save the fenced code to a temporary `.py` file
and run it there while keeping the working directory at the repository root.
No provider, network or authentic manuscript is involved.

The first full finding copies a precise reveal sentence. The second identifies a
structural absence and correctly omits the field. Two controls supply ambiguous
and nonverbatim values to exercise honest fallback, not endorsed producer output.

```python
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("plugins/apodictic/scripts").resolve()))
import annotation_manifest as am

snapshot = (
    "# Chapter 1\n"
    "The café clock rang.\n"
    "Mara opened the drawer and found the missing seal.\n"
    "The bell rang.\n"
    "# Chapter 2\n"
    "The bell rang.\n"
    "At dawn, the council accepted her claim.\n"
)
quote = "Mara opened the drawer and found the missing seal."
findings = [
    {
        "schema": "apodictic.finding.v1",
        "id": "F-P8-01",
        "mechanism": "The seal is identified before the scene's open question develops",
        "severity": "Should-Fix",
        "confidence": "MEDIUM",
        "evidence_refs": ["Pass 8 §Reveal Ledger", "Chapter 1"],
        "evidence_quote": quote,
        "fix_class": "reconsider reveal timing",
        "risk_if_fixed": "Delaying the reveal may obscure Mara's immediate objective",
    },
    {
        "schema": "apodictic.finding.v1",
        "id": "F-P8-02",
        "mechanism": "The council's acceptance has no earlier preparation across the chapter",
        "severity": "Should-Fix",
        "confidence": "MEDIUM",
        "evidence_refs": ["Pass 8 §Fairness Flags", "Chapter 2"],
        "fix_class": "review signpost distribution",
        "risk_if_fixed": "Additional cues may make the resolution predictable",
    },
]
for fid, value in [("F-P8-03", "The bell rang."),
                   ("F-P8-04", "Mara discovered the missing seal.")]:
    control = copy.deepcopy(findings[0])
    control.update(id=fid, evidence_refs=["Chapter 2"], evidence_quote=value)
    findings.append(control)

ledger = "# Findings Ledger\n" + "\n".join(
    "<!-- apodictic:finding\n" + json.dumps(f, ensure_ascii=False) + "\n-->"
    for f in findings
) + "\n"
assert "evidence_quote" not in findings[1]
# Validate the full finding blocks against the existing schema too.
schema = am.art.load_schema("apodictic.finding.v1")
for f in findings:
    assert not am.art.validate_obj(f, schema, "finding")
manifest, errors = am.build_manifest(snapshot, ledger, None,
    project="Invented", runlabel="demo", snapshot_path="snapshot.md")
assert not errors, errors
annotations = {a["finding_id"]: a for a in manifest["annotations"]}
start = snapshot.index(quote)
end = start + len(quote)
# These are Python character offsets, not UTF-8 byte offsets.
assert start != len(snapshot[:start].encode("utf-8"))
assert annotations["F-P8-01"]["anchor"] == {
    "kind": "quote", "value": f"{start}-{end}", "quote": quote}
assert snapshot[start:end] == quote
for fid in ["F-P8-02", "F-P8-03", "F-P8-04"]:
    assert annotations[fid]["anchor"] == {"kind": "chapter", "value": "Ch 2"}

annotated = am.render(snapshot, manifest)
comment = annotations["F-P8-01"]["comment"]
# The fixed finding-field comment follows the exact sentence, not the chapter.
assert quote + "{>>" + comment + "<<}" in annotated
assert am.reverse_transform(annotated) == snapshot
assert annotated.count("\n") == snapshot.count("\n")
def manifest_text(obj):
    return "<!-- apodictic:annotation\n" + json.dumps(obj) + "\n-->"
code, messages = am.check(snapshot, manifest_text(manifest), annotated,
                          ledger, None, strict=True)
assert code == 0, messages

# A6 protection means refusing a forged anchor, not rejecting honest fallback.
forged = copy.deepcopy(manifest)
forged["annotations"][0]["anchor"] = {
    "kind": "quote", "value": "0-9", "quote": "ABSENTXYZ"}
code, messages = am.check(snapshot, manifest_text(forged),
    am.render(snapshot, forged), ledger, None, strict=True)
assert code == 1 and any("A6 quote integrity" in m and "occurs 0" in m
                         for m in messages), messages
print("PASS: unique reveal, structural omission, ambiguous/nonverbatim fallback,")
print("exact character offsets, rendered placement, reverse transform, validation,")
print("and forged-anchor refusal (existing consumer only)")
```

The unique reveal reaches the `quote` rung. Structural omission and the two
invalid quote controls retain the existing `Chapter 2` anchor. The rendered
margin contains the fixed finding-field comment, not an inserted copy of the
quoted manuscript sentence. Removing the comment spans restores the snapshot.
The forged manifest is refused by A6; the honestly degraded manifests pass.
These observations establish no general sentence-precision or model capability
claim. Producer adherence requires a separate authorized evaluation.
