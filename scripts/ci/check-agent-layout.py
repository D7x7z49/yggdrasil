# @path[scripts/ci/check-agent-layout.py]
# check .agent directory structure, naming, and line budgets.
#
# rules:
# - .agent allows only AGENTS.md, experience, rule, and skill
# - experience and rule use two directory levels
# - skill uses three levels, the last one is a skill directory
# - a skill directory holds SKILL.md and optional scripts and references
# - directory names use kebab-case with 1-3 words, skill names with 2-5
# - experience files use .exp.md
# - rule markdown files use .rule.md
# - rule grammar files use .ebnf
# - file stems use kebab-case with 2-5 words
# - line budgets are reported as warnings, structure errors are fatal
#
# usage:
#   python scripts/ci/check-agent-layout.py [root]
#
# exit codes:
#   0 layout ok, warnings allowed
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
SKILL_ENTRY = "SKILL.md"

# key is the logical core, value is the on-disk directory name
CORE_DIRS = {
    "experience": "experience",
    "rule": "rule",
    "skill": "skill",
}

FILE_SUFFIXES = {
    "experience": (EXPERIENCE_SUFFIX,),
    "rule": (RULE_MD_SUFFIX, RULE_EBNF_SUFFIX),
}

SKILL_DIRS = ("references", "scripts")

DIR_WORD_RANGE = (1, 3)
FILE_WORD_RANGE = (2, 5)

# line budgets: a rule is read in one pass, an experience can be re-read,
# a skill is read once before acting, a payload file is read on demand.
LINE_LIMITS = {
    "experience": (12, 48),
    "rule": (8, 24),
    "grammar": (0, 300),
    "skill": (20, 60),
    "payload": (0, 300),
}

MESSAGES = {
    "cli.run.description": "check the .agent directory layout and naming rules",
    "cli.run.root_help": "agent root to check, defaulting to .agent",
    "usage.path.invalid": "root path must be a real directory at [{root}]",
    "runtime.scan.io_error": "cannot scan [{path}] because of [{error}]",
    "layout.root.unexpected": "unexpected root entry",
    "layout.core.missing": "core directory is missing or invalid",
    "layout.core.file": "only target directories are allowed at the core level",
    "layout.target.file": "only aspect directories are allowed at the target level",
    "layout.aspect.subdir": "subdirectories are not allowed at the aspect level",
    "layout.aspect.skill_file": "only skill directories are allowed at the aspect level",
    "layout.entry.symlink": "symlink is not allowed",
    "layout.entry.unsupported": "unsupported entry",
    "layout.name.dir_kebab": "directory name must use lower-case kebab-case",
    "layout.name.dir_words": "directory name must have {min_words}-{max_words} words",
    "layout.name.file_suffix": "{core} file must end with {allowed}",
    "layout.name.file_kebab": "file stem must use lower-case kebab-case",
    "layout.name.file_words": "file stem must have {min_words}-{max_words} words",
    "layout.skill.missing": "skill directory must contain SKILL.md",
    "layout.skill.entry": "skill directory allows only SKILL.md, scripts, and references",
    "layout.name.skill_words": "skill name must have {min_words}-{max_words} words",
    "layout.line.range": "{kind} file must have {min_lines}-{max_lines} lines, got [{count}]",
    "layout.line.max": "{kind} file must have at most {max_lines} lines, got [{count}]",
    "layout.file.encoding": "file must be utf-8 text",
    "report.layout.ok": "layout ok at [{root}]",
    "report.layout.summary": "[{count}] layout errors at [{root}]",
    "report.layout.warn_summary": "[{count}] line warnings at [{root}]",
    "report.layout.error": "[{path}] {message}",
    "report.layout.warning": "[{path}] {message}",
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


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def relative(self, path: Path) -> Path:
        try:
            return path.relative_to(self.root)
        except ValueError:
            return path

    def error(self, path: Path, text: str) -> None:
        text = message("report.layout.error", path=self.relative(path), message=text)
        self.errors.append(text)

    def warn(self, path: Path, text: str) -> None:
        text = message("report.layout.warning", path=self.relative(path), message=text)
        self.warnings.append(text)


# ==============================================================================
# LAYOUT CHECKS
# ==============================================================================


def check_name(report: Report, path: Path) -> None:
    if not is_kebab(path.name):
        report.error(path, message("layout.name.dir_kebab"))
        return

    min_words, max_words = DIR_WORD_RANGE
    count = word_count(path.name)
    if not min_words <= count <= max_words:
        text = message(
            "layout.name.dir_words",
            min_words=min_words,
            max_words=max_words,
        )
        report.error(path, text)


def check_lines(report: Report, kind: str, path: Path) -> None:
    min_lines, max_lines = LINE_LIMITS[kind]
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.error(path, message("layout.file.encoding"))
        return

    count = len(content.splitlines())
    if min_lines <= count <= max_lines:
        return

    if min_lines == 0:
        text = message("layout.line.max", kind=kind, max_lines=max_lines, count=count)
    else:
        text = message(
            "layout.line.range",
            kind=kind,
            min_lines=min_lines,
            max_lines=max_lines,
            count=count,
        )
    report.warn(path, text)


def file_kind(core: str, suffix: str) -> str:
    if core == "experience":
        return "experience"
    if suffix == RULE_EBNF_SUFFIX:
        return "grammar"
    return "rule"


def check_file(report: Report, core: str, path: Path) -> None:
    stem = strip_file_suffix(core, path.name)
    if stem is None:
        allowed = " or ".join(FILE_SUFFIXES[core])
        text = message("layout.name.file_suffix", core=core, allowed=allowed)
        report.error(path, text)
        return

    if not is_kebab(stem):
        report.error(path, message("layout.name.file_kebab"))
        return

    min_words, max_words = FILE_WORD_RANGE
    count = word_count(stem)
    if not min_words <= count <= max_words:
        text = message(
            "layout.name.file_words",
            min_words=min_words,
            max_words=max_words,
        )
        report.error(path, text)
        return

    suffix = path.name.removeprefix(stem)
    check_lines(report, file_kind(core, suffix), path)


def check_payload(report: Report, base: Path) -> None:
    for path in sorted(base.rglob("*")):
        if path.is_symlink():
            report.error(path, message("layout.entry.symlink"))
            continue
        if path.is_file():
            check_lines(report, "payload", path)


def check_skill_entry(report: Report, entry: Path) -> None:
    if not is_kebab(entry.name):
        report.error(entry, message("layout.name.dir_kebab"))
    else:
        min_words, max_words = FILE_WORD_RANGE
        if not min_words <= word_count(entry.name) <= max_words:
            text = message(
                "layout.name.skill_words",
                min_words=min_words,
                max_words=max_words,
            )
            report.error(entry, text)

    skill_file = entry / SKILL_ENTRY
    if not skill_file.is_symlink():
        if skill_file.is_file():
            check_lines(report, "skill", skill_file)
        else:
            report.error(entry, message("layout.skill.missing"))

    for path in sorted(entry.iterdir()):
        if path.is_symlink():
            report.error(path, message("layout.entry.symlink"))
            continue
        if path.name == SKILL_ENTRY:
            continue
        if path.is_dir() and path.name in SKILL_DIRS:
            check_payload(report, path)
            continue
        report.error(path, message("layout.skill.entry"))


def check_aspect(report: Report, core: str, aspect: Path) -> None:
    if core == "skill":
        for path in sorted(aspect.iterdir()):
            if path.is_symlink():
                report.error(path, message("layout.entry.symlink"))
                continue
            if not path.is_dir():
                report.error(path, message("layout.aspect.skill_file"))
                continue
            check_skill_entry(report, path)
        return

    for path in sorted(aspect.iterdir()):
        if path.is_symlink():
            report.error(path, message("layout.entry.symlink"))
            continue
        if path.is_dir():
            report.error(path, message("layout.aspect.subdir"))
            continue
        if not path.is_file():
            report.error(path, message("layout.entry.unsupported"))
            continue
        check_file(report, core, path)


def check_target(report: Report, core: str, target: Path) -> None:
    check_name(report, target)

    for aspect in sorted(target.iterdir()):
        if aspect.is_symlink():
            report.error(aspect, message("layout.entry.symlink"))
            continue
        if not aspect.is_dir():
            report.error(aspect, message("layout.target.file"))
            continue
        check_name(report, aspect)
        check_aspect(report, core, aspect)


def check_core(report: Report, core: str, directory: str) -> None:
    base = report.root / directory
    if not base.is_dir() or base.is_symlink():
        report.error(base, message("layout.core.missing"))
        return

    for target in sorted(base.iterdir()):
        if target.is_symlink():
            report.error(target, message("layout.entry.symlink"))
            continue
        if not target.is_dir():
            report.error(target, message("layout.core.file"))
            continue
        check_target(report, core, target)


def check_root(report: Report) -> None:
    # AGENTS.md is the only non-core root entry
    allowed = {"AGENTS.md", *CORE_DIRS.values()}
    for path in sorted(report.root.iterdir()):
        if path.name not in allowed:
            report.error(path, message("layout.root.unexpected"))

    for core, directory in CORE_DIRS.items():
        check_core(report, core, directory)


def check_layout(root: Path) -> Report:
    report = Report(root)
    check_root(report)
    return report


# ==============================================================================
# REPORTING
# ==============================================================================


def report_result(report: Report) -> int:
    for warning in report.warnings:
        print(warning, file=sys.stderr)
    if report.warnings:
        text = message(
            "report.layout.warn_summary",
            root=report.root,
            count=len(report.warnings),
        )
        print(text, file=sys.stderr)

    if not report.errors:
        print(message("report.layout.ok", root=report.root))
        return EXIT_OK

    for error in report.errors:
        print(error, file=sys.stderr)
    text = message(
        "report.layout.summary",
        root=report.root,
        count=len(report.errors),
    )
    print(text, file=sys.stderr)
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
        report = check_layout(args.root)
    except OSError as exc:
        print(message("runtime.scan.io_error", path=args.root, error=exc), file=sys.stderr)
        return EXIT_IO
    return report_result(report)


if __name__ == "__main__":
    raise SystemExit(main())
