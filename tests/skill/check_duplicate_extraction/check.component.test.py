# @path[tests/skill/check_duplicate_extraction/check.component.test.py]
# contract tests for the extraction judgment command

import json
from pathlib import Path

import pytest

# ==============================================================================
# CONSTANTS
# ==============================================================================

SCRIPT = ".agent/skill/code/refactor/check-duplicate-extraction/scripts/check.py"

# ==============================================================================
# HELPERS
# ==============================================================================


def project(tmp_path: Path, copies: int) -> dict:
    # all sources share one directory, so each costs one path step
    shared = tmp_path / "pkg/shared"
    shared.mkdir(parents=True)
    sources = []
    for index in range(copies):
        (shared / f"f{index}.py").write_text("x\n", encoding="utf-8")
        sources.append(f"shared/f{index}.py")
    return {
        "root": "pkg",
        "target": {"path": "shared/dup.py", "added": True},
        "sources": sources,
    }


def run(check, tmp_path: Path, task: dict, capsys) -> tuple[int, str]:
    path = tmp_path / "task.json"
    path.write_text(json.dumps(task), encoding="utf-8")
    code = check.main([str(path), "--project", str(tmp_path)])
    return code, capsys.readouterr().out.strip()


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture(scope="module")
def check(load_script):
    return load_script(SCRIPT)


# ==============================================================================
# CASES
# ==============================================================================


def test_true_verdict(check, tmp_path, capsys) -> None:
    code, out = run(check, tmp_path, project(tmp_path, 5), capsys)
    assert code == 0
    assert out == "true"


def test_false_verdict(check, tmp_path, capsys) -> None:
    code, out = run(check, tmp_path, project(tmp_path, 2), capsys)
    assert code == 0
    assert out == "false"


def test_invalid_input(check, tmp_path, capsys) -> None:
    task = project(tmp_path, 2)
    task["sources"].append("../outside.py")
    code, out = run(check, tmp_path, task, capsys)
    assert code == 2
    assert out == ""


def test_missing_task(check, tmp_path) -> None:
    code = check.main([str(tmp_path / "missing.json"), "--project", str(tmp_path)])
    assert code == 3
