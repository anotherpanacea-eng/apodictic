"""Native hashing needs neither PATH nor an external hash provider."""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "plugins/apodictic/scripts/validate.py"


def test_native_hash_bytes_with_no_external_tools(tmp_path):
    contract = tmp_path / "-contract with spaces.md"
    contract.write_bytes(b"contract\r\nbytes\n")
    digest = hashlib.sha256(contract.read_bytes()).hexdigest()
    env = {**os.environ, "PATH": "", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    def run(*args):
        return subprocess.run([sys.executable, str(VALIDATOR), *args], cwd=tmp_path,
                              env=env, capture_output=True, text=True, encoding="utf-8")
    assert run("contract-hash", contract.name).stdout == digest + "\n"
    assert run("contract-check", contract.name, digest).returncode == 0
    assert run("contract-check", contract.name, "0" * 64).returncode == 1


def test_posix_compatibility_shim_names_missing_python(tmp_path):
    bash = shutil.which("bash")
    if os.name == "nt" or not bash:
        pytest.skip("POSIX compatibility seam; native hashing test runs everywhere")
    # The shim uses only Bash builtins until the Python exec.
    result = subprocess.run([bash, str(ROOT / "scripts/validate.sh"), "contract-hash", "unused"],
                            env={**os.environ, "PATH": ""}, capture_output=True)
    assert result.returncode == 127
    assert result.stdout == b""
    assert b"Python 3.10+" in result.stderr
