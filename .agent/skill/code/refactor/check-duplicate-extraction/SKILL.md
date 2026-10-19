---
name: check-duplicate-extraction
description: >
  judge whether duplicate functions, classes, types, or interfaces belong in
  one shared file. use during a refactor or a reuse extraction, after the
  caller confirms the copies are semantically identical.
---

SCOPE
- apply to one duplicate set per run
- apply inside one package root chosen by the caller
- trust the caller's root and duplicate confirmation
- measure lookup cost, shared change benefit, and traversal cost
- return one boolean and leave the edit to the caller

INPUT
- provide one json object as a file or on stdin

```json
{
  "root": "packages/a",
  "target": { "path": "src/shared/dup.py", "added": true },
  "sources": ["src/x.py", "src/y.py"]
}
```

- `root`: package root, relative to the project root
- `target`: destination object
  - `path`: shared file, relative to `root`
  - `added`: true when the file is new
- `sources`: files holding the copies, relative to `root`
- `root` bounds every path

OUTPUT
- print one line, `true` or `false`
- when stderr is not empty, treat the run as failed
- true means one shared file at `target.path`
- false means the copies remain separate
- a single source file returns false

SCRIPT
- run `scripts/check.py task.json` from the project root
- pass the same object on stdin with `scripts/check.py -`

WORKFLOW
- confirm the copies are semantically identical
- choose a package root allowed by the project
- collect the destination path and the source files
- run the script on the json file
- read the boolean from stdout
- when the result is true, consolidate into `target.path`
- when the result is false, keep the copies
