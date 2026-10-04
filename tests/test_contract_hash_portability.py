"""contract-hash/check on a host with sha256sum but no shasum (e.g. Git Bash)."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess

import pytest

VALIDATOR = Path(__file__).resolve().parents[1] / "scripts/validate.sh"


def test_sha256sum_fallback_and_missing_provider_fails_closed(tmp_path):
    tools = {n: shutil.which(n) for n in ("bash", "dirname", "awk", "sha256sum")}
    if os.name == "nt" or not all(tools.values()):
        pytest.skip("needs bash, dirname, awk and sha256sum")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("bash", "dirname", "awk"):
        (bin_dir / name).symlink_to(tools[name])
    contract = tmp_path / "-contract.md"
    contract.write_bytes(b"contract\r\nbytes\n")
    digest = hashlib.sha256(contract.read_bytes()).hexdigest()

    def run(*args):
        return subprocess.run([tools["bash"], str(VALIDATOR), *args], cwd=tmp_path,
                              env={"PATH": str(bin_dir)}, capture_output=True, text=True)

    # No provider at all: neither a digest nor an "unchanged" verdict.
    for args in (("contract-hash", "-contract.md"), ("contract-check", "-contract.md", "")):
        result = run(*args)
        assert (result.returncode, result.stdout) == (127, ""), result.stderr

    (bin_dir / "sha256sum").symlink_to(tools["sha256sum"])
    assert run("contract-hash", "-contract.md").stdout == digest + "\n"
    assert run("contract-check", "-contract.md", digest).returncode == 0
