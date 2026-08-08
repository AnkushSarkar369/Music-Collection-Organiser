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

    print("\n" + "=" * 58)
    print("  BRACKET TAG REPORT")
    print("=" * 58)
    print(f"  Scanning: {ROOT}")
    print("-" * 58)

    for file in ROOT.rglob("*"):
        if not file.is_file():
            continue

        for match in PATTERN.findall(file.stem):
            tag = match.strip()
            counts[tag] += 1
            names[tag].append(file.name)

    if not counts:
        print("  No square-bracket tags found.")
        print("=" * 58 + "\n")
        return

    print(f"  Found {sum(counts.values())} tag occurrence(s) across {len(counts)} unique tag(s).\n")

    for tag in sorted(counts, key=str.casefold):
        print(f"  [{tag}]  ({counts[tag]} occurrence(s))")
        for name in sorted(names[tag], key=str.casefold):
            print(f"      {name}")
        print()

    print("=" * 58)
    print("  Report complete.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
