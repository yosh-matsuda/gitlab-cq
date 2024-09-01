from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

from gitlab_cq.mypy import parse

if TYPE_CHECKING:
    from gitlab_cq import GitLabCodeQuality

mypy_json_str: Final[
    str
] = """{"file": "{file_path}", "line": 898, "column": 16, "message": "List comprehension has incompatible type List[Result | None]; expected List[Promise]", "hint": null, "code": "misc", "severity": "error"}
{"file": "{file_path}", "line": 890, "column": 16, "message": "List comprehension has incompatible type List[Result | None]; expected List[Promise]", "hint": null, "code": "misc", "severity": "error"}
{"file": "{file_path}", "line": 891, "column": 16, "message": "List comprehension has incompatible type List[Result | None]; expected List[Promise]", "hint": null, "code": "misc", "severity": "error"}
""".replace("{file_path}", str(Path(__file__).resolve().relative_to(Path.cwd())))


mypy_issues: Final[list[GitLabCodeQuality.Issue]] = [
    {
        "type": "issue",
        "check_name": "mypy: misc",
        "description": "List comprehension has incompatible type List[Result | None]; expected List[Promise]",
        "categories": ["Style"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 898, "column": 16}, "end": {"line": 898, "column": 16}},
        },
        "severity": "minor",
        "fingerprint": "d1776315ccd7cedf0995551a826b22d7",
    },
    {
        "type": "issue",
        "check_name": "mypy: misc",
        "description": "List comprehension has incompatible type List[Result | None]; expected List[Promise]",
        "categories": ["Style"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 890, "column": 16}, "end": {"line": 890, "column": 16}},
        },
        "severity": "minor",
        "fingerprint": "c3c3bdd0e7dc6c09a199dd83964b4472",
    },
    {
        "type": "issue",
        "check_name": "mypy: misc",
        "description": "List comprehension has incompatible type List[Result | None]; expected List[Promise]",
        "categories": ["Style"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 891, "column": 16}, "end": {"line": 891, "column": 16}},
        },
        "severity": "minor",
        "fingerprint": "251d5a6119a57c83dec7c7d970c51e93",
    },
]

mypy_json_str_with_warn = (
    """ * Install prebuilt node (22.7.0) ../root/.local/share/virtualenvs/amplify-WmOJONDV/lib/python3.12/site-packages/nodeenv.py:639: DeprecationWarning: Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.
  archive.extractall(src_dir, extract_list)
... done.
"""
    + mypy_json_str
)


def test_mypy_empty() -> None:
    assert parse("") == []


def test_mypy() -> None:
    assert parse(mypy_json_str) == mypy_issues
    assert parse(mypy_json_str_with_warn) == mypy_issues
