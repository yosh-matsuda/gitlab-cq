from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypedDict

from . import GitLabCodeQuality


class _LocationOrEndLocation(TypedDict):
    column: int
    row: int


class _Edit(TypedDict):
    content: str
    end_location: _LocationOrEndLocation
    location: _LocationOrEndLocation


class _Fix(TypedDict):
    applicability: str
    edits: list[_Edit]
    message: str


class _RuffOutputJson(TypedDict):
    cell: None | int
    code: str
    end_location: _LocationOrEndLocation
    filename: str
    fix: None | _Fix
    location: _LocationOrEndLocation
    message: str
    noqa_row: int
    url: str


def parse(linter_output: str) -> list[GitLabCodeQuality.Issue]:
    # extract JSON body
    match = re.search(r"(^\[.*|(?<=\n)\[.*)$", linter_output, re.DOTALL)
    if not match:
        raise ValueError(
            "No JSON body found in the output\n"
            "Hint: argument `--output-format json` is required and do not set `--output`\nOutput:\n" + linter_output
        )

    gitlab_code_quality: list[GitLabCodeQuality.Issue] = []
    try:
        ruff_output_json: list[_RuffOutputJson] = json.loads(match.group())
        for obj in ruff_output_json:
            issue: GitLabCodeQuality.Issue = {
                "type": "issue",
                "check_name": "Ruff: " + obj["code"],
                "description": obj["message"],
                "content": {"body": "[" + obj["code"] + "](" + obj["url"] + ")"},
                "categories": ["Style"],
                "location": {
                    "path": str(Path(obj["filename"]).relative_to(Path.cwd())),
                    "positions": {
                        "begin": {"line": obj["location"]["row"], "column": obj["location"]["column"]},
                        "end": {"line": obj["end_location"]["row"], "column": obj["end_location"]["column"]},
                    },
                },
                "severity": "minor",
            }
            GitLabCodeQuality.add_fingerprint(issue)
            gitlab_code_quality.append(issue)
    except json.JSONDecodeError as e:
        raise ValueError(
            "Hint: argument `--output-format json` is required and do not set `--output`\nOutput:\n" + linter_output
        ) from e

    return gitlab_code_quality
