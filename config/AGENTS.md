<!-- @path[config/AGENTS.md] -->
<!-- NOTE: map for the config directory -->

PURPOSE
- hold repository configuration outside source, tests, and agent knowledge
- cover inputs for ci, toolchain, build, and repository checks
- keep one concern per file

FILES
- `root.list` holds package roots for repository checks
- each file describes its own syntax in its header

ADDING
- create one file per concern
- document it in its header, then add it to FILES
