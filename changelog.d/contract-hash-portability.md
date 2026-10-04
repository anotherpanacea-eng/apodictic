### Portable contract digests

Fall back to `sha256sum` for `contract-hash` / `contract-check` when `shasum` is
unavailable (perl-less Linux, some Git Bash installs). The file is hashed via
stdin, so names beginning with `-` are read literally.
