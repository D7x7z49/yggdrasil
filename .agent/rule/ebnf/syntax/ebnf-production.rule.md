<!-- @path[.agent/rule/ebnf/syntax/ebnf-production.rule.md] -->
<!-- production layout, indentation, and terminals for the ebnf subset -->

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

---
