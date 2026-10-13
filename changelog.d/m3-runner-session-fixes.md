### Validator development runner sessions

The development JSONL runner no longer ends healthy sessions after 64 frames, 16 MiB, 600 seconds or 60 idle seconds. A validation sent while another runs now waits in order instead of receiving `busy`, a queued request can be cancelled before it starts, and clean EOF finishes the active and queued work, so a piped batch returns every result. Per-request text, output, five-second execution and cleanup limits are unchanged.
