# @path[tests/e2e/hi.e2e.test.py]
# smoke test that the e2e project is wired

from pathlib import Path


def test_hi() -> None:
    assert Path(__file__).parent.name == "e2e"
