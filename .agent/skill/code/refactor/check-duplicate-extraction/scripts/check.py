# @path[.agent/skill/code/refactor/check-duplicate-extraction/scripts/check.py]
# judge whether duplicate declarations belong in one shared file.
#
# usage:
#   python3 check.py task.json
#   python3 check.py -
#
# exit codes:
#   0 judgment printed
#   2 invalid input
#   3 filesystem error

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# ==============================================================================
# CONSTANTS
# ==============================================================================

EXIT_OK = 0
EXIT_INPUT = 2
EXIT_IO = 3

TASK_FIELDS = {"root", "target", "sources"}
TARGET_FIELDS = {"path", "added"}

# a deeper upward search is far outside any real repository layout
MAX_PARENT_STEPS = 20

# ==============================================================================
# MESSAGES
# ==============================================================================

MESSAGES = {
    "cli.description": "judge one duplicate extraction",
    "cli.task_help": "json file, or - for stdin",
    "cli.project_help": "project root",
    "task.object": "task must be a json object",
    "task.field_unknown": "unknown field [{field}]",
    "root.empty": "root must be a non-empty string",
    "root.missing": "root is not a directory at [{path}]",
    "target.object": "target must be an object",
    "target.field_unknown": "unknown target field [{field}]",
    "target.path": "target.path must be a non-empty string",
    "target.added": "target.added must be a boolean",
    "target.file": "target is not a file at [{path}]",
    "target.parent": "target parent is missing at [{path}]",
    "target.overlap": "target appears in sources",
    "sources.type": "sources must be a list of strings",
    "source.file": "source is not a file at [{path}]",
    "path.escape": "[{label}] escapes root at [{path}]",
    "path.absolute": "[{label}] must be relative at [{path}]",
    "path.parent": "[{label}] must stay inside the base at [{path}]",
    "path.symlink": "[{label}] is a symlink at [{path}]",
    "path.depth": "target is [{count}] levels above the source",
    "json.invalid": "invalid json at [{error}]",
    "text.encoding": "task must be utf-8 text",
    "fs.error": "filesystem error at [{error}]",
}


def message(key: str, **values: object) -> str:
    return MESSAGES[key].format(**values)


# ==============================================================================
# TYPES
# ==============================================================================


class InputError(Exception):
    pass


@dataclass(frozen=True)
class ExtractionTarget:
    path: str
    added: bool


@dataclass(frozen=True)
class ExtractionTask:
    root: str
    target: ExtractionTarget
    sources: tuple[str, ...]


# ==============================================================================
# PARSING
# ==============================================================================


def parse_task(raw: object) -> ExtractionTask:
    if not isinstance(raw, dict):
        raise InputError(message("task.object"))

    unknown = set(raw) - TASK_FIELDS
    if unknown:
        raise InputError(message("task.field_unknown", field=sorted(unknown)[0]))

    root = raw.get("root")
    if not isinstance(root, str) or not root:
        raise InputError(message("root.empty"))

    raw_target = raw.get("target")
    if not isinstance(raw_target, dict):
        raise InputError(message("target.object"))

    unknown = set(raw_target) - TARGET_FIELDS
    if unknown:
        raise InputError(message("target.field_unknown", field=sorted(unknown)[0]))

    path = raw_target.get("path")
    if not isinstance(path, str) or not path:
        raise InputError(message("target.path"))

    added = raw_target.get("added")
    if not isinstance(added, bool):
        raise InputError(message("target.added"))

    raw_sources = raw.get("sources")
    if not isinstance(raw_sources, list) or not all(isinstance(item, str) for item in raw_sources):
        raise InputError(message("sources.type"))

    target = ExtractionTarget(path, added)
    return ExtractionTask(root, target, tuple(raw_sources))


def load_task(source: str) -> ExtractionTask:
    if source == "-":
        text = sys.stdin.read()
    else:
        text = Path(source).read_text(encoding="utf-8")
    return parse_task(json.loads(text))


# ==============================================================================
# PATHS
# ==============================================================================


def resolve_relative(base: Path, text: str, label: str) -> Path:
    relative = PurePosixPath(text)
    if relative.is_absolute():
        raise InputError(message("path.absolute", label=label, path=text))
    if ".." in relative.parts:
        raise InputError(message("path.parent", label=label, path=text))

    candidate = base
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise InputError(message("path.symlink", label=label, path=text))

    resolved = candidate.resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise InputError(message("path.escape", label=label, path=text))
    return resolved


def resolve_root(project: Path, text: str) -> Path:
    root = resolve_relative(project, text, "root")
    if not root.is_dir():
        raise InputError(message("root.missing", path=text))
    return root


def source_files(root: Path, texts: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for text in texts:
        path = resolve_relative(root, text, "source")
        if not path.is_file():
            raise InputError(message("source.file", path=text))
        files.append(path)
    return files


def relative_parts(path: Path, root: Path) -> tuple[str, ...]:
    return path.relative_to(root).parts


def common_prefix(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    count = 0
    while count < min(len(left), len(right)) and left[count] == right[count]:
        count += 1
    return count


# ==============================================================================
# COST
# ==============================================================================


def path_cost(root: Path, target_dir: Path, source_dirs: list[Path]) -> int:
    target_parts = relative_parts(target_dir, root)
    total = 0
    for source_dir in source_dirs:
        source_parts = relative_parts(source_dir, root)
        common = common_prefix(target_parts, source_parts)
        up = len(target_parts) - common
        down = len(source_parts) - common
        if up > MAX_PARENT_STEPS:
            raise InputError(message("path.depth", count=up))
        exponent = down if up == 0 else 2**up + down
        total += 2**exponent
    return total


def structure_cost(root: Path, target_dir: Path, added: bool) -> int:
    total = 1
    current = target_dir
    while current != root:
        # hidden entries stay out, matching a plain ls
        count = sum(1 for entry in os.scandir(current) if not entry.name.startswith("."))
        if added and current == target_dir:
            count += 1
        # a chain through a hidden directory can leave zero visible entries
        count = max(1, count)
        total *= count
        current = current.parent
    return total


# ==============================================================================
# DECISION
# ==============================================================================


def decide(task: ExtractionTask, project: Path) -> bool:
    root = resolve_root(project, task.root)

    target = resolve_relative(root, task.target.path, "target")
    if target.exists() and not target.is_file():
        raise InputError(message("target.file", path=task.target.path))
    if not target.parent.is_dir():
        raise InputError(message("target.parent", path=task.target.path))

    sources = source_files(root, task.sources)
    unique = sorted(set(sources))
    if target in unique:
        raise InputError(message("target.overlap"))
    if len(unique) <= 1:
        return False

    target_dir = target.parent
    source_dirs = [source.parent for source in unique]
    benefit = 2 ** (len(unique) - 1)
    lookup = path_cost(root, target_dir, source_dirs)
    traversal = structure_cost(root, target_dir, task.target.added)
    return lookup - benefit + traversal < 0


# ==============================================================================
# COMMAND LINE
# ==============================================================================


def fail(code: int, text: str) -> int:
    print(text, file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=message("cli.description"))
    parser.add_argument("task", help=message("cli.task_help"))
    parser.add_argument("--project", type=Path, default=Path.cwd(), help=message("cli.project_help"))
    args = parser.parse_args(argv)

    try:
        task = load_task(args.task)
        result = decide(task, args.project)
    except InputError as exc:
        return fail(EXIT_INPUT, str(exc))
    except json.JSONDecodeError as exc:
        return fail(EXIT_INPUT, message("json.invalid", error=exc))
    except UnicodeDecodeError:
        return fail(EXIT_IO, message("text.encoding"))
    except OSError as exc:
        return fail(EXIT_IO, message("fs.error", error=exc))

    print("true" if result else "false")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
