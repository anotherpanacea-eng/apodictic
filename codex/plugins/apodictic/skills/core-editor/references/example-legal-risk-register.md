# Legal Risk Register: A Quiet Year (memoir)

<!--
Worked example of a contract-conformant Legal Risk Register (Legal Risk Register workflow; see
legal-risk-register.md + docs/legal-risk-register.md). The register FLAGS areas of a memoir /
autofiction / nonfiction manuscript that may warrant legal review — defamation, privacy/disclosure,
rights-clearance — each with a legal-escalation severity (monitor / review-recommended / review-now)
and an escalation trigger. It is NOT legal advice and never adjudicates (the module firewall: flag,
don't practice law).

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`legal-risk` (L1 schema, L2 unique ids, L3 not-a-lawyer disclaimer present; W1 no legal-advice
drift, W2 review-now routed to counsel). Keep `concern`/`disposition` as FLAGS, never legal
conclusions ("a factual claim about a named living person — flag for review", not "this is not
defamatory").
-->

**I am not a lawyer.** This register flags areas that may need legal review before publication; it is **not legal advice**. Where an item is marked `review-now`, consult qualified counsel.

## Register

<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-01","risk_class":"defamation","severity":"review-now","subject":"the narrator's former manager (named; current, identifiable employer)","locations":["Ch. 4","Ch. 9 (p. 212)"],"concern":"a stated-as-fact assertion that a named, living person committed financial wrongdoing","escalation_trigger":"any retained statement of fact (not clearly framed opinion) alleging a crime or professional misconduct by a named living person","disposition":"route to legal counsel before publication; substantiate or reframe as disclosed opinion"}
-->

<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-02","risk_class":"privacy","severity":"review-recommended","subject":"the narrator's sister (identifiable; private medical history disclosed)","locations":["Ch. 6"],"concern":"disclosure of a private, non-public health matter about an identifiable living person who has not consented","escalation_trigger":"private facts about an identifiable living person, not of legitimate public concern, that they have not consented to disclose","disposition":"flag for legal review; consider consent, anonymization, or composite treatment"}
-->

<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-03","risk_class":"rights-clearance","severity":"monitor","subject":"song lyrics quoted as an epigraph","locations":["epigraph","Ch. 2"],"concern":"reproduction of copyrighted song lyrics may require permission from the rights holder","escalation_trigger":"any quoted copyrighted text (lyrics, poetry, substantial prose) reproduced beyond incidental reference","disposition":"flag for permissions review; track for clearance or replacement before final"}
-->

## Notes

- **Severity is a legal-escalation tier**, kept separate from the editorial Must/Should/Could scale: `monitor` (track), `review-recommended` (raise with the author), `review-now` (route to counsel before publication).
- The register identifies *areas* and *triggers*; the legal judgment itself belongs to a qualified attorney.
