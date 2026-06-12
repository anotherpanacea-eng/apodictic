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
{"schema":"apodictic.legal_risk.v1","id":"LR-01","risk_class":"defamation","severity":"review-now","subject":"the narrator's former manager (named; current, identifiable employer)","locations":["Ch. 4","Ch. 9 (p. 212)"],"concern":"a stated-as-fact assertion that a named, living person committed financial wrongdoing","escalation_trigger":"DEF_SERIOUS_ALLEGATION_PRIVATE +serious-allegation — a retained statement of fact (not clearly framed opinion) alleging a crime or professional misconduct by a named living person","disposition":"route to legal counsel before publication; substantiate or reframe as disclosed opinion"}
-->

<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-02","risk_class":"privacy","severity":"review-now","subject":"the narrator's sister (identifiable; private medical history disclosed)","locations":["Ch. 6"],"concern":"disclosure of a private, non-public health matter about an identifiable living person who has not consented","escalation_trigger":"PRIV_INTIMATE_PRIVATE +identifiable-living-private-person — intimate non-public health facts about an identifiable living person, disclosed without consent","disposition":"route to legal counsel before publication; consider consent, anonymization, or composite treatment"}
-->

<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-03","risk_class":"rights-clearance","severity":"review-now","subject":"song lyrics quoted as an epigraph","locations":["epigraph","Ch. 2"],"concern":"reproduction of copyrighted song lyrics may require permission from the rights holder","escalation_trigger":"CR_LYRICS_POETRY_UNPUB — copyrighted song lyrics reproduced (here as an epigraph) without a licence","disposition":"route to legal / permissions counsel before publication; clear the licence or replace the epigraph before final"}
-->

<!-- apodictic:legal_risk
{"schema":"apodictic.legal_risk.v1","id":"LR-04","risk_class":"rights-clearance","severity":"monitor","subject":"a real consumer brand named in passing narrative (no endorsement implied)","locations":["Ch. 3"],"concern":"an ordinary in-narrative mention of a real brand — flagged only to confirm it stays out of the title, cover, and marketing","escalation_trigger":"TM_NOMINATIVE — ordinary brand mention in narrative (lower exposure; the flagged risk is marketing / cover / merchandise use, which this is not)","disposition":"monitor; no action unless the brand moves into the title, cover, or promotional copy"}
-->

## Notes

- **Severity is a legal-escalation tier**, kept separate from the editorial Must/Should/Could scale: `monitor` (track), `review-recommended` (raise with the author), `review-now` (route to counsel before publication). Here LR-01–LR-03 each hit a `review-now` bright line of the §Escalation-trigger taxonomy (serious allegation about a named living person; intimate health facts disclosed without consent; unlicensed lyrics) and so route to counsel; LR-04 is a nominative brand mention — `monitor` only, since the exposure attaches to marketing/cover use, not in-narrative reference. Memoir legal exposure tends to cluster at the high tier once the detection taxonomy is applied.
- Each `escalation_trigger` leads with a §Escalation-trigger taxonomy code (plus any tier-raising modifiers), per the module Protocol; the tier shown matches that code's default tier.
- The register identifies *areas* and *triggers*; the legal judgment itself belongs to a qualified attorney.
