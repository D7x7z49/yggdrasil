<!-- @path[.agent/AGENTS.md] -->
<!-- NOTE: map for understanding and viewing the .agent directory -->

PURPOSE
- this file is the reading map for `.agent`
- it explains layout, reading order, and category boundaries
- it does not replace the rule files

LAYOUT
- `.agent` has two directories, `experience` and `rule`
- `AGENTS.md` is the only root file
- every entry uses two levels, target then aspect

PATH
- locate an entry by target and aspect
- use the file suffix to identify the category
- use `.exp.md` for experience
- use `.rule.md` or `.ebnf` for rule

READING
- read this map first
- read the central rule before a tool rule
- read a tool rule before experience
- read experience only when context matters
- read grammar only when shape or format matters

EXPERIENCE
- treat experience as episodic, contextual, and stateful
- use it for evidence, precedent, and background
- do not treat it as a normative rule

RULE
- treat rule as normative, abstract, and stateless or class-state
- use it for action and validation
- let rule win when rule and experience conflict

GRAMMAR
- treat grammar as structure, not behavior
- use `rule/ebnf/syntax/` for the notation
- use `rule/core/format/` for document shape

REFERENCES
- `rule/core/agent/` for global agent behavior and writing rules
- `rule/core/format/` for experience and rule formats
- `rule/ebnf/syntax/` for grammar and style

---
