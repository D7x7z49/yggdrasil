<!-- @path[tests/README.md] -->
<!-- test conventions for yggdrasil -->

PURPOSE
- verify necessary conditions only
- no suite covers infinite input space
- focus on high-importance inputs
- rely on monitoring and fast rollback for untested areas

SCOPE
- cover project-global code, such as the root scripts
- cover consistency between project-global tools
- keep a subproject's tests inside that subproject
- keep end-to-end flows in a separate project
- do not mirror subprojects under this directory

LAYOUT
- project root code by area, so `scripts/ci` maps to `tests/ci`
- strip the source prefix and keep the area
- convert hyphens to underscores
- name a file after the module and the level, as `check_agent_layout.unit.test.py`
- use the suffix for the level, not a directory
- keep cross-area fixtures in `tests/conftest.py`
- keep area setup in the test file
- add a directory conftest only when two files share setup
- load hyphenated scripts through `load_script`

DATA
- keep each case under `tests/data/<area>/<case>/`
- use `project/` for the input tree
- store expected output only when the case checks it
- keep exit codes in the test code
- keep data paths in `conftest.py`

LEVELS
- `*.unit.test.py`: one branch per test, no external calls
- `*.component.test.py`: main scenarios and critical errors of one interface
- `*.integration.test.py`: only combinations the product uses
- `*.e2e.test.py`: five to fifteen flows with direct impact
- keep this suffix scheme for python files only

RULES
- test one contract per test
- assert the exit code, stdout, or stderr
- use literal expectations
- call only the command entry point, not private helpers
- keep setup visible in the test file
- write tests when the interface is stable

BUDGET
- keep test code under 40 percent of production code
- keep `conftest.py` under 30 percent of test code
- keep fixture chains at two levels or less

RUNNING
- run `uv run --locked pytest`
- run `make check` for the layout and hook gate

LIMITS
- do not treat coverage as a goal
- do not test the tools that run the tests
- this approach does not suit safety-critical systems
