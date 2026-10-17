<!-- @path[.agent/experience/dev/decision/comment-scope.exp.md] -->
<!-- NOTE: comment only the knowledge that code cannot carry. -->

STEP.
- classify a function as decomposition or reuse before choosing its scope
- keep a decomposition function private and local to its caller
- extract a reuse function only after two or more identical instances exist
- treat a docstring as an interface document, not as a default comment
- prefer a single-line comment when the code already states the signature and behavior
- comment only non-obvious intent, constraints, side effects, or invariants
- remove a comment that repeats a name, parameter list, or control flow
- use a header comment for file scope and rules
- use a block comment for a logical section
- use an inline comment for a local ambiguity
- record an experience only when the lesson generalizes beyond one script

NOTE.
- a docstring can duplicate the signature and become stale with the code
- a comment that repeats code adds maintenance cost without adding knowledge
- a function name and a small body are often the clearest documentation
- a project may require docstrings when it exposes a public API or generated reference
- keep the comment level proportional to the reader's need
- keep the reason and the constraint near the code they govern

---
