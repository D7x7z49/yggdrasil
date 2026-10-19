# @path[scripts/tools/check-duplicate-extraction.py]
# check the task root against config/root.list, then run the judgment.
#
# usage:
#   python3 scripts/tools/check-duplicate-extraction.py task.json
#   python3 scripts/tools/check-duplicate-extraction.py -
#
# exit codes:
#   0 judgment printed
#   2 invalid input or unlisted root
#   3 task or root list cannot be read

import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

# ==============================================================================
# CONSTANTS
# ==============================================================================

EXIT_INPUT = 2
EXIT_IO = 3

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / ".agent/skill/code/refactor/check-duplicate-extraction/scripts/check.py"
LIST = ROOT / "config/root.list"

# ==============================================================================
# MESSAGES
# ==============================================================================

MESSAGES = {
    "usage": "usage at [scripts/tools/check-duplicate-extraction.py] takes one task",
    "root.unlisted": "root is not listed at [config/root.list] for [{root}]",
    "task.unreadable": "cannot read task at [{error}]",
    "roots.unreadable": "cannot read root list at [config/root.list] because of [{error}]",
}

# ==============================================================================
# TYPES
# ==============================================================================


class InputError(Exception):
    pass


# ==============================================================================
# TASK
# ==============================================================================


def read_text(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def task_root(text: str) -> str | None:
    # a malformed task is left to the skill to report
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    root = data.get("root")
    return root if isinstance(root, str) else None


# ==============================================================================
# ROOTS
# ==============================================================================


def normalized(text: str) -> str:
    return PurePosixPath(text.strip()).as_posix()


def read_roots() -> set[str]:
    try:
        text = LIST.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(MESSAGES["roots.unreadable"].format(error=exc))

    roots = set()
    for line in text.splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        roots.add(normalized(entry))
    return roots


# ==============================================================================
# COMMAND LINE
# ==============================================================================


def main() -> int:
    if len(sys.argv) != 2:
        print(MESSAGES["usage"], file=sys.stderr)
        return EXIT_INPUT

    try:
        text = read_text(sys.argv[1])
    except OSError as exc:
        print(MESSAGES["task.unreadable"].format(error=exc), file=sys.stderr)
        return EXIT_IO

    root = task_root(text)
    if root is not None:
        try:
            roots = read_roots()
        except InputError as exc:
            print(exc, file=sys.stderr)
            return EXIT_IO
        if normalized(root) not in roots:
            print(MESSAGES["root.unlisted"].format(root=root), file=sys.stderr)
            return EXIT_INPUT

    return subprocess.run(
        [sys.executable, str(CHECK), "-"],
        input=text,
        cwd=ROOT,
        text=True,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
