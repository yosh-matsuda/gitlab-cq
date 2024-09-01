from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest
from gitlab_cq.ruff import parse

if TYPE_CHECKING:
    from gitlab_cq import GitLabCodeQuality

ruff_json_str: Final[str] = """[
  {
    "cell": null,
    "code": "F401",
    "end_location": {
      "column": 12,
      "row": 3
    },
    "filename": "{file_path}",
    "fix": {
      "applicability": "safe",
      "edits": [
        {
          "content": "",
          "end_location": {
            "column": 1,
            "row": 4
          },
          "location": {
            "column": 1,
            "row": 3
          }
        }
      ],
      "message": "Remove unused import: `json`"
    },
    "location": {
      "column": 8,
      "row": 3
    },
    "message": "`json` imported but unused",
    "noqa_row": 3,
    "url": "https://docs.astral.sh/ruff/rules/unused-import"
  }
]
""".replace("{file_path}", str(Path(__file__).resolve()))

ruff_issues: Final[list[GitLabCodeQuality.Issue]] = [
    {
        "type": "issue",
        "check_name": "Ruff: F401",
        "description": "`json` imported but unused",
        "content": {"body": "[F401](https://docs.astral.sh/ruff/rules/unused-import)"},
        "categories": ["Style"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 3, "column": 8}, "end": {"line": 3, "column": 12}},
        },
        "severity": "minor",
        "fingerprint": "5219c42860a91ccbc6a888f345364775",
    }
]

ruff_json_str_with_warn = (
    """ * Install prebuilt node (22.7.0) ../root/.local/share/virtualenvs/amplify-WmOJONDV/lib/python3.12/site-packages/nodeenv.py:639: DeprecationWarning: Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.
  archive.extractall(src_dir, extract_list)
... done.
"""
    + ruff_json_str
)


def test_ruff_empty() -> None:
    output = ""
    with pytest.raises(ValueError):
        parse(output)


def test_ruff_no_error() -> None:
    output = "[]"
    assert parse(output) == []


def test_ruff() -> None:
    assert parse(ruff_json_str) == ruff_issues
    assert parse(ruff_json_str_with_warn) == ruff_issues
