# @path[tests/tools/check_duplicate_extraction.integration.test.py]
# integration test for the wrapper and the judgment script

import subprocess
import sys

# ==============================================================================
# CONSTANTS
# ==============================================================================

SCRIPT = "scripts/tools/check-duplicate-extraction.py"

# ==============================================================================
# CASES
# ==============================================================================


def test_invalid_task(repo_root, tmp_path) -> None:
    task = tmp_path / "task.json"
    task.write_text("{\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(repo_root / SCRIPT), str(task)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    assert "invalid json" in proc.stderr
