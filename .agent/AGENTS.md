<!-- @path[.agent/AGENTS.md] -->
<!-- NOTE: map for understanding and viewing the .agent directory -->

PURPOSE
- this file is the reading map for `.agent`
- it explains layout, reading order, and category boundaries
- it does not replace the rule files

LAYOUT
- `.agent` has three directories, `experience`, `rule`, and `skill`
- `AGENTS.md` is the only root file
- experience and rule entries are files, placed at target then aspect
- a skill entry is a directory, placed at target then aspect, then skill name
- a skill directory holds `SKILL.md`

PATH
- use the file suffix to identify experience and rule
- use `.exp.md` for experience
- use `.rule.md` or `.ebnf` for rule
- locate a skill by target, aspect, then skill name
- a skill directory holds `SKILL.md` and optional `scripts/` and `references/`

READING
- read this map first
- read the central rule before a tool rule
- read a tool rule before experience
- read experience only when context matters
- read grammar only when shape or format matters
- read a skill only when its description matches the task

EXPERIENCE
- treat experience as episodic, contextual, and stateful
- use it for evidence, precedent, and background
- do not treat it as a normative rule

RULE
- treat rule as normative, abstract, and stateless or class-state
- use it for action and validation
- let rule win when rule and experience conflict

SKILL
- treat skill as procedural and situational, not normative
- use it for the task at hand, not for general policy
- keep the deterministic part in `scripts/` and detail in `references/`
- let rule win when a skill and a rule conflict

GRAMMAR
- treat grammar as structure, not behavior
- use `rule/ebnf/syntax/` for the notation
- use `rule/core/format/` for document shape

REFERENCES
- `rule/core/agent/` for global agent behavior and writing rules
- `rule/core/format/` for experience and rule formats
- `rule/ebnf/syntax/` for grammar and style

---
