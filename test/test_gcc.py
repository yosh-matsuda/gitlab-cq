from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest
from gitlab_cq.gcc import parse

if TYPE_CHECKING:
    from gitlab_cq import GitLabCodeQuality

gcc_output_str: Final[str] = """{file_path}:453:17: warning: 'switch' missing 'default' label [-Wswitch-default]
  453 |                 switch (xxx)
      |                 ^
1 warning generated.
{file_path}:41:28: warning: implicit conversion changes signedness: 'int' to 'size_type' (aka 'unsigned long') [-Wsign-conversion]
   41 |         EXPECT_TRUE(xxx[i].size() == N - 2);
      |                     ~~~~~~ ^
{file_path}:1823:50: note: expanded from macro 'EXPECT_TRUE'
 1823 | #define EXPECT_TRUE(condition) GTEST_EXPECT_TRUE(condition)
      |                                                  ^~~~~~~~~
{file_path}:1808:23: note: expanded from macro 'GTEST_EXPECT_TRUE'
 1808 |   GTEST_TEST_BOOLEAN_(condition, #condition, false, true, \
      |                       ^~~~~~~~~
{file_path}:1453:38: note: expanded from macro 'GTEST_TEST_BOOLEAN_'
 1453 |           ::testing::AssertionResult(expression))                     \
      |                                      ^~~~~~~~~~
{file_path}:39:24: warning: comparison of integers of different signs: 'int' and 'IndexType' (aka 'unsigned int') [-Wsign-compare]
   39 |     for (auto i = 1; i < N - 1; i++)
      |                      ~ ^ ~~~~~
2 warnings generated.
In file included from {file_path}:3:
In file included from {file_path}:4:
{file_path}:453:17: warning: 'switch' missing 'default' label [-Wswitch-default]
  453 |                 switch (xxx)
      |                 ^
1 warning generated.
""".replace("{file_path}", str(Path(__file__).resolve()))


gcc_issues: Final[list[GitLabCodeQuality.Issue]] = [
    {
        "type": "issue",
        "check_name": "gcc: -Wswitch-default",
        "description": "'switch' missing 'default' label",
        "categories": ["Bug Risk"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 453, "column": 17}, "end": {"line": 453, "column": 17}},
        },
        "severity": "major",
        "fingerprint": "9c4775cae5499784d55682db1d384ced",
    },
    {
        "type": "issue",
        "check_name": "gcc: -Wsign-conversion",
        "description": "implicit conversion changes signedness: 'int' to 'size_type' (aka 'unsigned long')",
        "categories": ["Bug Risk"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 41, "column": 28}, "end": {"line": 41, "column": 28}},
        },
        "severity": "major",
        "fingerprint": "ce05830ad965dc8ab362c5ff5ef41655",
    },
    {
        "type": "issue",
        "check_name": "gcc: -Wsign-compare",
        "description": "comparison of integers of different signs: 'int' and 'IndexType' (aka 'unsigned int')",
        "categories": ["Bug Risk"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 39, "column": 24}, "end": {"line": 39, "column": 24}},
        },
        "severity": "major",
        "fingerprint": "1598d3db95670684e5ffa77509e5a7e9",
    },
    {
        "type": "issue",
        "check_name": "gcc: -Wswitch-default",
        "description": "'switch' missing 'default' label",
        "categories": ["Bug Risk"],
        "location": {
            "path": str(Path(__file__).relative_to(Path.cwd())),
            "positions": {"begin": {"line": 453, "column": 17}, "end": {"line": 453, "column": 17}},
        },
        "severity": "major",
        "fingerprint": "9c4775cae5499784d55682db1d384ced",
    },
]


def test_gcc_empty() -> None:
    assert parse("", "gcc", "major") == []


def test_gcc() -> None:
    assert parse(gcc_output_str, "gcc", "major") == gcc_issues
