from __future__ import annotations

import json
from itertools import dropwhile
from pathlib import Path
from typing import Literal, TypedDict

from . import GitLabCodeQuality


class _MypyOutputJson(TypedDict):
    file: str
    line: int
    column: int
    message: str
    hint: str
    code: str
    severity: Literal["error", "note"]


def parse(linter_output: str) -> list[GitLabCodeQuality.Issue]:
    gitlab_code_quality: list[GitLabCodeQuality.Issue] = []
    try:
        for line in dropwhile(lambda line: not line.startswith("{"), linter_output.splitlines()):
            # skip empty lines
            if not line:
                continue

            obj: _MypyOutputJson = json.loads(line)

            # skip notes
            if obj["severity"] == "note":
                continue

            issue: GitLabCodeQuality.Issue = {
                "type": "issue",
                "check_name": "mypy: " + obj["code"],
                "description": obj["message"],
                "categories": ["Style"],
                "location": {
                    "path": str(Path(obj["file"])),
                    "positions": {
                        "begin": {"line": obj["line"], "column": obj["column"]},
                        "end": {"line": obj["line"], "column": obj["column"]},
                    },
                },
                "severity": "minor",
            }
            GitLabCodeQuality.add_fingerprint(issue)
            gitlab_code_quality.append(issue)
    except json.JSONDecodeError as e:
        raise ValueError(e.msg + "\nHint: argument `--output=json` is required\nOutput:\n" + linter_output) from e

    return gitlab_code_quality
