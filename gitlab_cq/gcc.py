from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final, Literal

from . import GitLabCodeQuality

MESSAGE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^(?P<path>.+):(?P<line>\d+):(?P<column>\d+): (?P<severity>\S+): (?P<message>.*?)( \[(?P<diagnostic>.*)\])?$"
)


def parse(
    linter_output: str, name: str, severity: Literal["info", "minor", "major", "critical", "blocker"]
) -> list[GitLabCodeQuality.Issue]:
    result: list[GitLabCodeQuality.Issue] = []
    for line in linter_output.splitlines():
        regex_result = MESSAGE_REGEX.match(line)
        if regex_result is None or regex_result.group("severity") == "note":
            continue
        try:
            issue: GitLabCodeQuality.Issue = {
                "type": "issue",
                "check_name": f"{name}: " + regex_result.group("diagnostic"),
                "description": regex_result.group("message"),
                "categories": ["Bug Risk"],
                "location": {
                    "path": str(Path(regex_result.group("path")).relative_to(Path.cwd())),
                    "positions": {
                        "begin": {"line": int(regex_result.group("line")), "column": int(regex_result.group("column"))},
                        "end": {"line": int(regex_result.group("line")), "column": int(regex_result.group("column"))},
                    },
                },
                "severity": severity,
            }
            GitLabCodeQuality.add_fingerprint(issue)
            result.append(issue)
        except Exception as e:  # noqa: BLE001
            print(f"Error: {e}", file=sys.stderr)
    return result
