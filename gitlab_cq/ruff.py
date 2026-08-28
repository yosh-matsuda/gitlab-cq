from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypedDict

from typing_extensions import NotRequired

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
    cell: int | None
    code: str | None
    end_location: _LocationOrEndLocation
    filename: str
    fix: _Fix | None
    location: _LocationOrEndLocation
    message: str
    name: NotRequired[str]
    noqa_row: int | None
    url: str | None


def parse(linter_output: str) -> list[GitLabCodeQuality.Issue]:
    # extract JSON body
    match = re.search(r"(^\[.*|(?<=\n)\[.*)$", linter_output, re.DOTALL)
    if not match:
        raise ValueError(
            "No JSON body found in the output\n"
            "Hint: argument `--output-format json` is required and do not set `--output`\nOutput:\n" + linter_output
        )

    try:
        ruff_output_json: list[_RuffOutputJson] = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(
            "Hint: argument `--output-format json` is required and do not set `--output`\nOutput:\n" + linter_output
        ) from e

    gitlab_code_quality: list[GitLabCodeQuality.Issue] = []
    for obj in ruff_output_json:
        # `code` is null for a syntax error and for a preview rule that has no code assigned
        # yet, and `url` is null whenever the rule has no documentation page. `name` holds the
        # rule in both cases, so it is the fallback for the check name.
        rule = obj["code"] or obj.get("name") or ""
        url = obj["url"]
        issue: GitLabCodeQuality.Issue = {
            "type": "issue",
            "check_name": "Ruff: " + rule if rule else "Ruff",
            "description": obj["message"],
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
        if rule and url:
            issue["content"] = {"body": "[" + rule + "](" + url + ")"}
        GitLabCodeQuality.add_fingerprint(issue)
        gitlab_code_quality.append(issue)

    return gitlab_code_quality
