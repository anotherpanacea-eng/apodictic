### Native Python validator utilities

Added `validate.py` for contract hashing/checking, state line counting, ledger
structure, artifact naming, synthesis sections and tone checks. Raw-byte hashing
and LF counting require no external tools; existing Python parsers retain their
CLI behavior. Exact-byte differential checks compare the seven utilities against
the Bash dispatcher. Remaining commands and aggregates still use `validate.sh`;
the continuation roadmap records the later cutover and Windows acceptance.
