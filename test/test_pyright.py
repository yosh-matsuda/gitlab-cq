from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest
from gitlab_cq.pyright import parse

if TYPE_CHECKING:
    from gitlab_cq import GitLabCodeQuality

pyright_json_str: Final[str] = """{
    "version": "1.1.378",
    "time": "1725119710426",
    "generalDiagnostics": [
        {
            "file": "{file_path}",
            "severity": "error",
            "message": "Overload 5 for \\"Test\\" will never be used because its parameters overlap overload 4",
            "range": {
                "start": {
                    "line": 6763,
                    "character": 8
                },
                "end": {
                    "line": 6763,
                    "character": 18
                }
            },
            "rule": "reportOverlappingOverload"
        }
    ],
    "summary": {
        "filesAnalyzed": 1,
        "errorCount": 1,
        "warningCount": 0,
        "informationCount": 0,
        "timeInSec": 7.561
    }
}
""".replace("{file_path}", str(Path(__file__).resolve()))

pyright_issues: Final[list[GitLabCodeQuality.Issue]] = [
    {
        "type": "issue",
        "check_name": "Pyright: reportOverlappingOverload",
        "description": 'Overload 5 for "Test" will never be used because its parameters overlap overload 4',
        "content": {
            "body": "[reportOverlappingOverload](https://github.com/microsoft/pyright/blob/main/docs/configuration.md#reportOverlappingOverload)"
        },
        "categories": ["Style"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 6763, "column": 8}, "end": {"line": 6763, "column": 18}},
        },
        "severity": "minor",
        "fingerprint": "7bcb5e22c26fff8251f5e3eacfeaf269",
    }
]

pyright_json_empty: Final[str] = """{
    "version": "1.1.378",
    "time": "1725158437381",
    "generalDiagnostics": [],
    "summary": {
        "filesAnalyzed": 1,
        "errorCount": 0,
        "warningCount": 0,
        "informationCount": 0,
        "timeInSec": 0.628
    }
}"""

pyright_json_str_with_warn = (
    """ * Install prebuilt node (22.7.0) ../root/.local/share/virtualenvs/amplify-WmOJONDV/lib/python3.12/site-packages/nodeenv.py:639: DeprecationWarning: Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.
  archive.extractall(src_dir, extract_list)
... done.
"""
    + pyright_json_str
)


def test_pyright_empty() -> None:
    with pytest.raises(ValueError):
        parse("")


def test_pyright_no_error() -> None:
    assert parse(pyright_json_empty) == []


def test_pyright() -> None:
    assert parse(pyright_json_str) == pyright_issues
    assert parse(pyright_json_str_with_warn) == pyright_issues
