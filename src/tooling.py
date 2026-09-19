"""Tooling module for executing dynamic tests against generated code."""

import subprocess
import sys
import traceback
from pathlib import Path

# Paths relative to src/ (the CWD during execution)
PARSER_FILE = Path("parser.py")
TEST_FILE = Path("test_parser.py")
OUTPUT_DIR = Path("../output")

PYTEST_FLAGS = [
    "--html=../output/report.html",
    "--self-contained-html",
    "--log-file=../output/pytest_run.log",
    "--log-file-level=INFO",
    "-q",           # quiet: suppress per-test stdout chatter
    "--tb=short",   # compact tracebacks on failure
]


def execute_pytest(code: str, tests: str) -> str:
    """Execute pytest against the provided code and test suite.

    Writes *code* into ``parser.py`` and *tests* into ``test_parser.py``,
    runs ``pytest`` via subprocess, captures all output, and removes the
    temporary files afterwards.

    Args:
        code: Python source code to be tested (written to parser.py).
        tests: Pytest test code (written to test_parser.py).

    Returns:
        Combined stdout/stderr from the pytest run, or a formatted
        traceback if an unexpected exception occurs.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        PARSER_FILE.write_text(code, encoding="utf-8")
        TEST_FILE.write_text(tests, encoding="utf-8")

        # Always invoke pytest through the current interpreter so the venv
        # that launched main.py is used — avoids resolving a system pytest
        # that lacks project-local plugins like pytest-html.
        pytest_cmd = [sys.executable, "-m", "pytest"] + [str(TEST_FILE)] + PYTEST_FLAGS

        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        output = result.stdout or ""
        if result.stderr:
            output = f"{output}\n{result.stderr}"

        return output.strip()

    except Exception:
        return traceback.format_exc()

    finally:
        for path in (PARSER_FILE, TEST_FILE):
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
