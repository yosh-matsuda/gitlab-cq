from __future__ import annotations

import json
import subprocess  # noqa: S404
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, get_args

from .gcc import parse as parse_gcc
from .mypy import parse as parse_mypy
from .pyright import parse as parse_pyright
from .ruff import parse as parse_ruff

if TYPE_CHECKING:
    from . import GitLabCodeQuality

_SUPPORTED_LINTERS = Literal["ruff", "pyright", "mypy", "gcc", "clang-tidy", "clang"]
SUPPORTED_LINTERS: Final[tuple[_SUPPORTED_LINTERS, ...]] = get_args(_SUPPORTED_LINTERS)


def _parse_option_args(argv: list[str]) -> tuple[str, bool, bool]:
    output_file = ""
    merge = False
    echo = False

    while len(argv) > 0:
        if argv[0] == "--output":
            if len(argv) == 1 or argv[1].startswith("--"):
                print("No output file specified")
                sys.exit(1)
            output_file = argv[1]
            argv.pop(0)
            argv.pop(0)
        elif argv[0] == "--merge":
            merge = True
            argv.pop(0)
        elif argv[0] == "--echo":
            echo = True
            argv.pop(0)
        else:
            break

    if not output_file and (echo or merge):
        print("No output file specified with --echo or --merge")
        sys.exit(1)

    return output_file, merge, echo


def main() -> None:
    # parse arguments
    argv = sys.argv[1:]
    if len(argv) == 0:
        print(
            """
 GitLab-CQ: parse linter output and convert it to GitLab Code Quality report

Usage:

  Run linter command via. GitLab-CQ:
    $ python -m gitlab_cq [--output file_path] [--merge] [--echo] CMD [Arguments]

  Parse linter output from stdin:
    $ CMD [Arguments] | python -m gitlab_cq [--output file_path] [--merge] [--echo] LINTER

Arguments:
  CMD           Command to run linter
  Arguments     Arguments for linter command
  LINTER        Linter name to parse: {{{linters}}}

Options:
  --output file_path    Output to file_path
  --merge               Merge output to existing JSON file
                            (available if --output is specified)
  --echo                Echo linter output
                            (available if --output is specified)""".format(linters=", ".join(SUPPORTED_LINTERS))
        )
        sys.exit(1)

    # options
    linter: _SUPPORTED_LINTERS
    linter_output: str = ""
    output_file, merge, echo = _parse_option_args(argv)

    if not sys.stdin.isatty():
        # read from stdin

        def _tee(line: str) -> str:
            if echo:
                sys.stdout.write(line)
            return line

        linter_output = "".join(_tee(line) for line in sys.stdin)
        if len(argv) == 0:
            print("No command to run")
            sys.exit(1)

        linter = argv[0]  # type: ignore
        if linter not in SUPPORTED_LINTERS:
            print(f"Invalid linter name; {linter} is not supported")
            sys.exit(1)

    else:
        # run linter command
        cmd = argv[0]
        arguments = argv[1:]
        for name in SUPPORTED_LINTERS:
            if name in cmd:
                linter = name
                break
        else:
            # fallback to equivalent linter
            if "cmake" in cmd or "g++" in cmd:
                linter = "gcc"

            # linter not found
            print(f"Invalid linter command; {cmd} is not supported")
            sys.exit(1)

        # linter specific requirements in arguments
        req: list[str] = []
        if linter == "ruff":
            req = ["--output-format", "json"]
        elif linter == "pyright":
            req = ["--outputjson"]
        elif linter == "mypy":
            req = ["--output=json"]
        elif linter == "clang-tidy":
            req = ["--quiet"]
        if req and not any(arguments[i : i + len(req)] == req for i in range(len(arguments) - len(req) + 1)):
            # check if the linter has a subcommand
            if linter == "ruff":  # noqa: SIM108
                arguments = arguments[:1] + req + arguments[1:]
            else:
                arguments = req + arguments

        # run linter
        proc = subprocess.Popen(  # noqa: S603
            [cmd, *arguments], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", shell=False
        )
        while True:
            assert proc.stdout is not None
            line = proc.stdout.readline()
            if line:
                linter_output += line
                if echo:
                    sys.stdout.write(line)
            elif proc.poll() is not None:
                break

    # parse linter output
    issues: list[GitLabCodeQuality.Issue]
    if linter == "ruff":
        issues = parse_ruff(linter_output)
    elif linter == "pyright":
        issues = parse_pyright(linter_output)
    elif linter == "mypy":
        issues = parse_mypy(linter_output)
    elif linter == "clang-tidy":
        issues = parse_gcc(linter_output, linter, "minor")
    elif linter in {"gcc", "clang"}:
        issues = parse_gcc(linter_output, linter, "major")
    else:
        raise ValueError(f"linter {linter} is not supported")

    # write to output file
    if output_file:
        output_path = Path(output_file)
        if merge and output_path.exists() and output_path.stat().st_size > 0:
            with output_path.open("r") as f:
                issues = json.load(f) + issues
        with output_path.open("w") as f:
            json.dump(issues, f)
    else:
        print(json.dumps(issues))


if __name__ == "__main__":
    main()
