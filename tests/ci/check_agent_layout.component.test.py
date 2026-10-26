# @path[tests/ci/check_agent_layout.component.test.py]
# contract tests for the agent layout check

from pathlib import Path

import pytest

# ==============================================================================
# CONSTANTS
# ==============================================================================

SCRIPT = "scripts/ci/check-agent-layout.py"

# ==============================================================================
# HELPERS
# ==============================================================================


def doc_lines(title: str, prefix: str, count: int) -> str:
    # count includes the title line
    body = "".join(f"- {prefix} {index}\n" for index in range(1, count))
    return f"# {title}\n{body}"


def agent_tree(tmp_path: Path, *, skill: bool = True, rule_lines: int = 8) -> Path:
    root = tmp_path / ".agent"
    files = {
        "AGENTS.md": "# agents\n- sample map\n",
        "experience/dev/quality/sample-gate.exp.md": doc_lines("gate", "note", 12),
        "rule/core/agent/sample-rule.rule.md": doc_lines("rule", "rule", rule_lines),
        "skill/code/refactor/sample-skill/scripts/check.py": "x = 1\n",
    }
    if skill:
        files["skill/code/refactor/sample-skill/SKILL.md"] = doc_lines("skill", "step", 20)
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture(scope="module")
def layout(load_script):
    return load_script(SCRIPT)


# ==============================================================================
# CASES
# ==============================================================================


def test_valid_tree(layout, tmp_path) -> None:
    assert layout.main([str(agent_tree(tmp_path))]) == 0


def test_missing_skill_file(layout, tmp_path) -> None:
    assert layout.main([str(agent_tree(tmp_path, skill=False))]) == 1


def test_rule_budget_warning(layout, tmp_path, capsys) -> None:
    root = agent_tree(tmp_path, rule_lines=7)
    assert layout.main([str(root)]) == 0
    expected = layout.message("report.layout.warn_summary", count=1, root=root)
    assert expected in capsys.readouterr().err
