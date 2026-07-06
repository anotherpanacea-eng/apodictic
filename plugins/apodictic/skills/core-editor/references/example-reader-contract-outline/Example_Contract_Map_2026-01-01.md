# Contract Map — Example

This file is machine-read plumbing for the reader-contract reverse outline. It carries one apodictic.contract_map.v1 block: the ids-only localization of each contract clause to the scenes that establish and pay it off. It is gated (R7) before the outline projector consumes it; do not edit by hand.

<!-- apodictic:contract_map
{
  "schema": "apodictic.contract_map.v1",
  "inputs": {
    "pass0_sha256": "86e9942973c0f662e36e2768192324c8574390ebbfbd6927a72a923b933446f5",
    "contract_sha256": "f3e1a0de6f8ceb380e5f39350119d0ddf8e5d3dd2cfe64c7cb6ea306952add95",
    "ledger_sha256": "bb61c2f090264098c6ab68e0326ad7681bea4113c8d78a7eedba409d07267cc2"
  },
  "clauses": [
    {
      "clause_id": "C1",
      "source_field": "READER PROMISE",
      "clause_text": "a woman escapes a dying town",
      "established": ["S1"],
      "paid_off": ["S4"],
      "not_localizable": false,
      "gap_finding_id": null
    },
    {
      "clause_id": "C2",
      "source_field": "READER PROMISE",
      "clause_text": "the town's buried secret is exposed",
      "established": ["S3"],
      "paid_off": [],
      "not_localizable": false,
      "gap_finding_id": "F-PCF-02"
    },
    {
      "clause_id": "C3",
      "source_field": "CONTROLLING IDEA",
      "clause_text": "leaving costs more than staying, but staying costs the truth",
      "established": ["S1", "S2"],
      "paid_off": ["S4"],
      "not_localizable": false,
      "gap_finding_id": null
    },
    {
      "clause_id": "C4",
      "source_field": "NON-NEGOTIABLES",
      "clause_text": "the lighthouse stays unlit",
      "established": ["S3"],
      "paid_off": ["S4"],
      "not_localizable": false,
      "gap_finding_id": null
    },
    {
      "clause_id": "C5",
      "source_field": "NON-NEGOTIABLES",
      "clause_text": "Mara does not return to the valley",
      "established": [],
      "paid_off": [],
      "not_localizable": true,
      "gap_finding_id": null
    }
  ]
}
-->
