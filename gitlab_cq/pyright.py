from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal, TypedDict

from . import GitLabCodeQuality


class _LineCharacter(TypedDict):
    line: int
    character: int


class _Range(TypedDict):
    start: _LineCharacter
    end: _LineCharacter


class _GeneralDiagnostic(TypedDict):
    file: str
    severity: Literal["error", "warning", "information"]
    message: str
    range: _Range
    rule: str


class _Summary(TypedDict):
    filesAnalyzed: int
    errorCount: int
    warningCount: int
    informationCount: int
    timeInSec: float


class _PyrightOutputJson(TypedDict):
    version: str
    time: str
    generalDiagnostics: list[_GeneralDiagnostic]
    summary: _Summary


_UNDEFINED_RANGE: _Range = _Range(
    start=_LineCharacter(line=0, character=0),
    end=_LineCharacter(line=0, character=0),
)


def parse(linter_output: str) -> list[GitLabCodeQuality.Issue]:
    # extract JSON body
    match = re.search(r"(^{.*|(?<=\n){.*)$", linter_output, re.DOTALL)
    if not match:
        raise ValueError(
            "No JSON body found in the output\n" "Hint: argument `--outputjson` is required\nOutput:\n" + linter_output
        )

    gitlab_code_quality: list[GitLabCodeQuality.Issue] = []
    try:
        pyright_output_json: _PyrightOutputJson = json.loads(match.group(0))
        for obj in pyright_output_json["generalDiagnostics"]:
            # "range" key is optional - this behavior is not documented in
            # https://github.com/microsoft/pyright/blob/main/docs/command-line.md#json-output
            issue_range = obj.get("range", _UNDEFINED_RANGE)
            issue: GitLabCodeQuality.Issue = {
                "type": "issue",
                "check_name": "Pyright: " + obj["rule"],
                "description": obj["message"],
                "content": {
                    "body": "["
                    + obj["rule"]
                    + "](https://github.com/microsoft/pyright/blob/main/docs/configuration.md#"
                    + obj["rule"]
                    + ")"
                },
                "categories": ["Style"],
                "location": {
                    "path": str(Path(obj["file"]).relative_to(Path.cwd())),
                    "positions": {
                        # Pyright outputs zero-based line/character numbers; convert to one-based.
                        "begin": {
                            "line": issue_range["start"]["line"] + 1,
                            "column": issue_range["start"]["character"] + 1,
                        },
                        "end": {
                            "line": issue_range["end"]["line"] + 1,
                            "column": issue_range["end"]["character"] + 1,
                        },
                    },
                },
                "severity": "minor",
            }
            GitLabCodeQuality.add_fingerprint(issue)
            gitlab_code_quality.append(issue)
    except json.JSONDecodeError as e:
        raise ValueError(e.msg + "\nHint: argument `--outputjson` is required\nOutput:\n" + linter_output) from e

    return gitlab_code_quality
