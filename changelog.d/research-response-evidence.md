### Research verification

Citation resolution can now keep every parsed API response it read, used or not, and write them to a caller-chosen JSON file (`batch --response-evidence PATH`, or `resolve_batch(response_evidence_path=...)`). Each entry records the tier, whether the response was used, gave no match, or was not checked, and the time. Off by default; default output is unchanged.

Evidence distinguishes URL/archive absence from incomplete checks and retains malformed cached Wayback answers before retrying.
