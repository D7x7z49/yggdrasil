# @path[tests/tools/check_duplicate_extraction.component.test.py]
# contract tests for the root list gate

import json
from pathlib import Path

import pytest

# ==============================================================================
# CONSTANTS
# ==============================================================================

SCRIPT = "scripts/tools/check-duplicate-extraction.py"

# ==============================================================================
# HELPERS
# ==============================================================================


def prepare(wrapper, tmp_path: Path, monkeypatch, *, listed: bool, copies: int = 5) -> list[str]:
    shared = tmp_path / "pkg/shared"
    shared.mkdir(parents=True)
    sources = []
    for index in range(copies):
        (shared / f"f{index}.py").write_text("x\n", encoding="utf-8")
        sources.append(f"shared/f{index}.py")
    task = {
        "root": "pkg",
        "target": {"path": "shared/dup.py", "added": True},
        "sources": sources,
    }
    task_path = tmp_path / "task.json"
    task_path.write_text(json.dumps(task), encoding="utf-8")
    roots = tmp_path / "root.list"
    roots.write_text("# roots\npkg\n" if listed else "other\n", encoding="utf-8")
    # point the wrapper at the temporary project and root list
    monkeypatch.setattr(wrapper, "ROOT", tmp_path)
    monkeypatch.setattr(wrapper, "LIST", roots)
    return [str(task_path)]


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture(scope="module")
def wrapper(load_script):
    return load_script(SCRIPT)


# ==============================================================================
# CASES
# ==============================================================================


def test_listed_root(wrapper, tmp_path, monkeypatch, capfd) -> None:
    args = prepare(wrapper, tmp_path, monkeypatch, listed=True)
    assert wrapper.main(args) == 0
    assert capfd.readouterr().out.strip() == "true"


def test_unlisted_root(wrapper, tmp_path, monkeypatch, capfd) -> None:
    args = prepare(wrapper, tmp_path, monkeypatch, listed=False)
    assert wrapper.main(args) == 2
    expected = wrapper.MESSAGES["root.unlisted"].format(root="pkg")
    assert expected in capfd.readouterr().err


def test_missing_root_list(wrapper, tmp_path, monkeypatch) -> None:
    args = prepare(wrapper, tmp_path, monkeypatch, listed=True)
    monkeypatch.setattr(wrapper, "LIST", tmp_path / "missing.list")
    assert wrapper.main(args) == 3
