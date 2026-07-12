from __future__ import annotations

import sys
from pathlib import Path

import pytest


def main() -> int:
    """Run the PatternBuilder regression tests from the command line."""
    test_file = Path(__file__).resolve().with_name("tests.py")
    return pytest.main([str(test_file), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
