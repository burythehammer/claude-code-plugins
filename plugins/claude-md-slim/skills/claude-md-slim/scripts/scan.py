#!/usr/bin/env python3
"""Inventory a CLAUDE.md: per-section line counts for the slim audit.

Usage: python3 scan.py <path-to-CLAUDE.md> [--threshold 200]

Prints a table of sections (split on markdown headings), the line count of
each, a flag on sections over 30 lines, and a verdict on whether the file
exceeds the audit threshold. Headings inside fenced code blocks are ignored.
"""
import argparse
import re
import sys

SECTION_FLAG_LINES = 30


def scan(path: str, threshold: int) -> int:
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    total = len(lines)
    sections = []  # (level, title, start_line, line_count)
    current = [0, "(preamble)", 1]  # level, title, start
    in_fence = False
    fence_re = re.compile(r"^\s*(```|~~~)")
    heading_re = re.compile(r"^(#{1,6})\s+(.*)")

    def close(end_line: int) -> None:
        count = end_line - current[2] + 1
        if count > 0:
            sections.append((current[0], current[1], current[2], count))

    for i, line in enumerate(lines, start=1):
        if fence_re.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = heading_re.match(line)
        if m:
            close(i - 1)
            current = [len(m.group(1)), m.group(2).strip(), i]
    close(total)

    def tokens(start: int, count: int) -> int:
        chunk = lines[start - 1:start - 1 + count]
        return sum(len(l) + 1 for l in chunk) // 4  # ~4 chars per token

    width = max((len(t) for _, t, _, _ in sections), default=10)
    print(f"{'Section':<{width}}  {'Start':>5}  {'Lines':>5}  {'~Tokens':>7}  Flag")
    print(f"{'-' * width}  {'-' * 5}  {'-' * 5}  {'-' * 7}  ----")
    for level, title, start, count in sections:
        if title == "(preamble)" and count == 0:
            continue
        indent = "  " * max(level - 1, 0)
        label = f"{indent}{title}"[:width]
        flag = "LARGE" if count > SECTION_FLAG_LINES else ""
        print(f"{label:<{width}}  {start:>5}  {count:>5}  "
              f"{tokens(start, count):>7}  {flag}")

    print(f"\nTotal: {total} lines, ~{tokens(1, total)} tokens per session "
          f"({'OVER' if total > threshold else 'under'} the "
          f"{threshold}-line audit threshold)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--threshold", type=int, default=200)
    a = p.parse_args()
    sys.exit(scan(a.path, a.threshold))
