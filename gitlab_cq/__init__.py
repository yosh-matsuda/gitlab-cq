from __future__ import annotations

from hashlib import md5
from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .__version__ import __version__

__all__ = ["GitLabCodeQuality", "__version__"]


class GitLabCodeQuality:
    class LineColumn(TypedDict):
        line: int
        column: int

    class Position(TypedDict):
        begin: GitLabCodeQuality.LineColumn
        end: GitLabCodeQuality.LineColumn

    class Lines(TypedDict):
        begin: int
        end: int

    class Location(TypedDict):
        path: str
        positions: GitLabCodeQuality.Position

    class Location2(TypedDict):
        path: str
        lines: GitLabCodeQuality.Lines

    class Trace(TypedDict):
        locations: list[GitLabCodeQuality.Location | GitLabCodeQuality.Location2]
        stacktrace: NotRequired[bool]

    class Contents(TypedDict):
        body: str

    class Issue(TypedDict):
        type: Literal["issue"]
        check_name: str
        description: str
        content: NotRequired[GitLabCodeQuality.Contents]
        categories: list[
            Literal[
                "Bug Risk",
                "Clarity",
                "Compatibility",
                "Complexity",
                "Duplication",
                "Performance",
                "Security",
                "Style",
            ]
        ]
        location: GitLabCodeQuality.Location | GitLabCodeQuality.Location2
        trace: NotRequired[GitLabCodeQuality.Trace]
        other_locations: NotRequired[list[GitLabCodeQuality.Location | GitLabCodeQuality.Location2]]
        remediation_points: NotRequired[int]
        severity: NotRequired[Literal["info", "minor", "major", "critical", "blocker"]]
        fingerprint: NotRequired[str]

    @staticmethod
    def add_fingerprint(issue: GitLabCodeQuality.Issue) -> None:
        if issue["location"].get("lines") is not None:
            fingerprint = md5(  # noqa: S324
                (
                    issue["check_name"]
                    + issue["description"]
                    + issue["location"]["path"]
                    + str(issue["location"]["lines"]["begin"])  # type: ignore
                    + str(issue["location"]["lines"]["end"])  # type: ignore
                ).encode("utf-8")
            )
        elif issue["location"].get("positions") is not None:
            fingerprint = md5(  # noqa: S324
                (
                    issue["check_name"]
                    + issue["description"]
                    + issue["location"]["path"]
                    + str(issue["location"]["positions"]["begin"]["line"])  # type: ignore
                    + str(issue["location"]["positions"]["begin"]["column"])  # type: ignore
                    + str(issue["location"]["positions"]["end"]["line"])  # type: ignore
                    + str(issue["location"]["positions"]["end"]["column"])  # type: ignore
                ).encode("utf-8")
            )
        else:
            raise ValueError("could not find location")
        issue["fingerprint"] = fingerprint.hexdigest()
