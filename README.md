# GitLab-CQ

Parse linter output and convert it to [GitLab Code Quality](https://docs.gitlab.com/ee/ci/testing/code_quality.html) report.

## Supported Linters

*   [Ruff](https://docs.astral.sh/ruff/)
*   [Pyright](https://microsoft.github.io/pyright/#/)
*   [Mypy](https://mypy.readthedocs.io/en/stable/)
*   [GCC/Clang](https://gcc.gnu.org/)
*   [Clang-Tidy](https://clang.llvm.org/extra/clang-tidy/)

Pull Requests for additional linter support are welcome.

## Installation

```bash
$ python -m pip install -U gitlab-cq
```

Or use pipx:

```bash
$ pipx install gitlab-cq
```

## Usage

There are two ways to use GitLab-CQ: run linter command via. GitLab-CQ or parse linter output from stdin.

Run linter command via. GitLab-CQ:

```bash
$ gitlab-cq [--output file_path] [--merge] [--echo] CMD [Arguments]
```

Parse linter output from stdin:

```bash
$ CMD [Arguments] | gitlab-cq [--output file_path] [--merge] [--echo] LINTER
```

Arguments:

*   `CMD`:
    *   Command to run linter.
*   `Arguments`:
    *   Arguments for linter command.
*   `LINTER`:
    *   Linter name to parse: `{ruff, pyright, mypy, gcc, clang-tidy, clang}`

Options:

*   `--output file_path`:
    *   Output to file_path.
*   `--merge`:
    *   Merge output to existing JSON file (available if `--output` is specified).
*   `--echo`:
    *   Echo linter output (available if `--output` is specified).

### Required options for linters

The following options are required for linters when parsing from stdin.  
(No need to add the following when the linter runs via. GitLab-CQ, since these options are automatically added.)

*   `ruff`:
    *   `--output-format json` is required and do not pass `--output` option.
*   `pyright`:
    *   `--outputjson` is required.
*   `mypy`:
    *   `--output=json` is required.

## Example

Integration to GitLab CI and save an GitLab CQ artifact:

```yaml
code quality:
  stage: test
  script:
    # Run linters via. GitLab-CQ and merge output to gl-code-quality-report.json
    - pipx install gitlab-cq
    - gitlab-cq --output gl-code-quality-report.json         ruff check .
    - gitlab-cq --output gl-code-quality-report.json --merge pyright .
    - gitlab-cq --output gl-code-quality-report.json --merge mypy .
    # Parse linter/compiler output and merge to gl-code-quality-report.json
    - gcc -Wall -Wextra -o /dev/null -c main.c 2>&1     | gitlab-cq --output gl-code-quality-report.json --merge gcc
    - clang-tidy -format-style=file -p . --quiet main.c | gitlab-cq --output gl-code-quality-report.json --merge clang-tidy  
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
```

## Author

Yoshiki Matsuda (@yosh-matsuda)
