"""
Scans filenames for [bracketed] tags (e.g. [Remix], [2023]) and reports
how often each one appears, with the matching filenames.
Read-only — does not modify any files.
"""

from collections import Counter, defaultdict
import re

from config import ROOT

DESCRIPTION = "Report [bracketed] tags found in filenames"

PATTERN = re.compile(r"\[([^\[\]]+)\]")


def run():
    counts = Counter()
    names = defaultdict(list)

    for file in ROOT.rglob("*"):
        if not file.is_file():
            continue

        for match in PATTERN.findall(file.stem):
            tag = match.strip()
            counts[tag] += 1
            names[tag].append(file.name)

    if not counts:
        print("No square-bracket tags found.")
        return

    for tag in sorted(counts, key=str.casefold):
        print(f"[{tag}] ({counts[tag]})")
        for name in sorted(names[tag], key=str.casefold):
            print(f"  - {name}")
        print()


if __name__ == "__main__":
    run()