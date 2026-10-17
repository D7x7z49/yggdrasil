# @path[scripts/ci/check-agent-layout.py]
# check .agent directory structure and naming.
#
# rules:
# - .agent allows only AGENTS.md, experience, and rule
# - experience and rule use two directory levels
# - directory names use kebab-case with 1-3 words
# - experience files use .exp.md
# - rule markdown files use .rule.md
# - rule grammar files use .ebnf
# - file stems use kebab-case with 2-5 words
# - file contents are not checked
#
# usage:
#   python scripts/ci/check-agent-layout.py [root]
#
# exit codes:
#   0 layout ok
#   1 layout violations
#   2 usage error
#   3 io error

import argparse
import re
import sys
from pathlib import Path

# ==============================================================================
# CONSTANTS
# ==============================================================================

AGENT_ROOT = Path(".agent")
EXIT_OK = 0
EXIT_LAYOUT = 1
EXIT_USAGE = 2
EXIT_IO = 3

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPERIENCE_SUFFIX = ".exp.md"
RULE_MD_SUFFIX = ".rule.md"
RULE_EBNF_SUFFIX = ".ebnf"
FILE_SUFFIXES = {
    "experience": (EXPERIENCE_SUFFIX,),
    "rule": (RULE_MD_SUFFIX, RULE_EBNF_SUFFIX),
}
CORE_DIRS = tuple(FILE_SUFFIXES)

DIR_WORD_RANGE = (1, 3)
FILE_WORD_RANGE = (2, 5)

MESSAGES = {
    "cli.run.description": "check the .agent directory layout and naming rules",
    "cli.run.root_help": "agent root to check, defaulting to .agent",
    "usage.path.invalid": "root path must be a real directory: {root}",
    "runtime.scan.io_error": "cannot scan {path}: {error}",
    "layout.root.unexpected": "unexpected root entry",
    "layout.core.missing": "core directory is missing or invalid",
    "layout.core.file": "only target directories are allowed at the core level",
    "layout.target.file": "only aspect directories are allowed at the target level",
    "layout.aspect.subdir": "subdirectories are not allowed at the aspect level",
    "layout.entry.symlink": "symlink is not allowed",
    "layout.entry.unsupported": "unsupported entry",
    "layout.name.dir_kebab": "directory name must use lower-case kebab-case",
    "layout.name.dir_words": "directory name must have {min_words}-{max_words} words",
    "layout.name.file_suffix": "{core} file must end with {allowed}",
    "layout.name.file_kebab": "file stem must use lower-case kebab-case",
    "layout.name.file_words": "file stem must have {min_words}-{max_words} words",
    "report.layout.ok": "{root}: layout ok",
    "report.layout.summary": "{root}: {count} layout errors",
    "report.layout.error": "{path}: {message}",
}


# ==============================================================================
# HELPERS
# ==============================================================================


def is_kebab(name: str) -> bool:
    return bool(KEBAB_RE.fullmatch(name))


def word_count(name: str) -> int:
    return len(name.split("-"))


def strip_file_suffix(core: str, name: str) -> str | None:
    for suffix in FILE_SUFFIXES[core]:
        if name.endswith(suffix):
            return name.removesuffix(suffix)
    return None


def message(key: str, **values: object) -> str:
    return MESSAGES[key].format(**values)


# ==============================================================================
# LAYOUT CHECKS
# ==============================================================================


def add_error(errors: list[str], root: Path, path: Path, text: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = path
    errors.append(message("report.layout.error", path=relative, message=text))


def check_name(errors: list[str], root: Path, path: Path) -> None:
    if not is_kebab(path.name):
        add_error(errors, root, path, message("layout.name.dir_kebab"))
        return

    min_words, max_words = DIR_WORD_RANGE
    count = word_count(path.name)
    if not min_words <= count <= max_words:
        text = message(
            "layout.name.dir_words",
            min_words=min_words,
            max_words=max_words,
        )
        add_error(errors, root, path, text)


def check_file(errors: list[str], root: Path, core: str, path: Path) -> None:
    stem = strip_file_suffix(core, path.name)
    if stem is None:
        allowed = " or ".join(FILE_SUFFIXES[core])
        text = message("layout.name.file_suffix", core=core, allowed=allowed)
        add_error(errors, root, path, text)
        return

    if not is_kebab(stem):
        add_error(errors, root, path, message("layout.name.file_kebab"))
        return

    min_words, max_words = FILE_WORD_RANGE
    count = word_count(stem)
    if not min_words <= count <= max_words:
        text = message(
            "layout.name.file_words",
            min_words=min_words,
            max_words=max_words,
        )
        add_error(errors, root, path, text)


def check_aspect(errors: list[str], root: Path, core: str, aspect: Path) -> None:
    for path in sorted(aspect.iterdir()):
        if path.is_symlink():
            add_error(errors, root, path, message("layout.entry.symlink"))
            continue
        if path.is_dir():
            add_error(errors, root, path, message("layout.aspect.subdir"))
            continue
        if not path.is_file():
            add_error(errors, root, path, message("layout.entry.unsupported"))
            continue
        check_file(errors, root, core, path)


def check_target(errors: list[str], root: Path, core: str, target: Path) -> None:
    check_name(errors, root, target)

    for aspect in sorted(target.iterdir()):
        if aspect.is_symlink():
            add_error(errors, root, aspect, message("layout.entry.symlink"))
            continue
        if not aspect.is_dir():
            add_error(errors, root, aspect, message("layout.target.file"))
            continue
        check_name(errors, root, aspect)
        check_aspect(errors, root, core, aspect)


def check_core(errors: list[str], root: Path, core: str) -> None:
    base = root / core
    if not base.is_dir() or base.is_symlink():
        add_error(errors, root, base, message("layout.core.missing"))
        return

    for target in sorted(base.iterdir()):
        if target.is_symlink():
            add_error(errors, root, target, message("layout.entry.symlink"))
            continue
        if not target.is_dir():
            add_error(errors, root, target, message("layout.core.file"))
            continue
        check_target(errors, root, core, target)


def check_root(errors: list[str], root: Path) -> None:
    # AGENTS.md is the only non-core root entry
    allowed = {"AGENTS.md", *CORE_DIRS}
    for path in sorted(root.iterdir()):
        if path.name not in allowed:
            add_error(errors, root, path, message("layout.root.unexpected"))

    for core in CORE_DIRS:
        check_core(errors, root, core)


def check_layout(root: Path) -> list[str]:
    errors: list[str] = []
    check_root(errors, root)
    return errors


# ==============================================================================
# REPORTING
# ==============================================================================


def report(errors: list[str], root: Path) -> int:
    if not errors:
        print(message("report.layout.ok", root=root))
        return EXIT_OK

    for error in errors:
        print(error, file=sys.stderr)
    print(message("report.layout.summary", root=root, count=len(errors)), file=sys.stderr)
    return EXIT_LAYOUT


# ==============================================================================
# COMMAND LINE
# ==============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=message("cli.run.description"))
    parser.add_argument(
        "root",
        nargs="?",
        default=AGENT_ROOT,
        type=Path,
        help=message("cli.run.root_help"),
    )
    args = parser.parse_args(argv)
    if args.root.is_symlink() or not args.root.is_dir():
        print(message("usage.path.invalid", root=args.root), file=sys.stderr)
        return EXIT_USAGE

    try:
        errors = check_layout(args.root)
    except OSError as exc:
        print(message("runtime.scan.io_error", path=args.root, error=exc), file=sys.stderr)
        return EXIT_IO
    return report(errors, args.root)


if __name__ == "__main__":
    raise SystemExit(main())
