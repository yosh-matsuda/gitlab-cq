from __future__ import annotations

import json
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


def parse(linter_output: str) -> list[GitLabCodeQuality.Issue]:
    gitlab_code_quality: list[GitLabCodeQuality.Issue] = []
    try:
        pyright_output_json: _PyrightOutputJson = json.loads(linter_output)
        for obj in pyright_output_json["generalDiagnostics"]:
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
                        "begin": {"line": obj["range"]["start"]["line"], "column": obj["range"]["start"]["character"]},
                        "end": {"line": obj["range"]["end"]["line"], "column": obj["range"]["end"]["character"]},
                    },
                },
                "severity": "minor",
            }
            GitLabCodeQuality.add_fingerprint(issue)
            gitlab_code_quality.append(issue)
    except json.JSONDecodeError as e:
        raise ValueError("Hint: argument `--outputjson` is required\noutput:\n" + linter_output) from e

    return gitlab_code_quality
