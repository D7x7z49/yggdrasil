# @path[tests/hi.unit.test.py]
# smoke test that the test runner is wired

from pathlib import Path


def test_hi() -> None:
    assert Path(__file__).parent.name == "tests"
