<!-- @path[.agent/rule/ebnf/syntax/ebnf-format-style.rule.md] -->
<!-- NOTE: formatting choices for the ebnf subset. -->

VERSION
- use ebnf subset version 1
- treat `ebnf-subset-grammar.ebnf` as the source of truth for syntax
- treat this file as the source of truth for layout

LAYOUT
- put each production on its own block
- put the rule name on its own line
- indent `=` with two spaces
- put the expression after `=`
- put `;` on its own line with two spaces
- put each top-level alternative on its own `|` line with two spaces
- separate productions with one blank line

INDENTATION
- use two spaces
- do not use tabs
- keep comments at column zero

TERMINALS
- wrap literal text in double quotes
- wrap lexical descriptions in `? ... ?`
- keep comma separators as `, `
- keep spaces inside `[ ... ]`, `{ ... }`, and `( ... )`

COMMENTS
- use `(* ... *)`
- put comments on their own lines
- keep comment text lowercase
- use section comments for larger grammar groups

FILES
- start with a path comment
- state `ebnf subset version: 1`
- state the format rule
- end with one final newline

---
