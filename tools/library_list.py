"""
List songs by directory and report FLAC/Opus counts.
Read-only — does not modify any files.
"""

from collections import defaultdict

from config import ROOT

DESCRIPTION = "List library songs by directory"

AUDIO_EXTENSIONS = {".flac", ".opus"}


def collect_files():
    directories = defaultdict(lambda: {"flac": [], "opus": []})

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in AUDIO_EXTENSIONS:
            continue

        relative = file.relative_to(ROOT)
        parts = relative.parts[:-1]
        directory = " - ".join(parts)

        if file.suffix.lower() == ".flac":
            directories[directory]["flac"].append(file.stem)
        else:
            directories[directory]["opus"].append(file.stem)

    return directories


def run():
    directories = collect_files()

    print("\n" + "=" * 58)
    print("  LIBRARY SONG LIST")
    print("=" * 58)
    print(f"  Library: {ROOT}")
    print("=" * 58 + "\n")

    if not directories:
        print("  No FLAC or Opus files found.\n")
        return

    for directory in sorted(directories, key=str.casefold):
        print(f"[{directory}]")

        songs = directories[directory]["flac"] + directories[directory]["opus"]
        for song in sorted(songs, key=str.casefold):
            print(f"  {song}")

        print()

    rows = []
    for directory in sorted(directories, key=str.casefold):
        opus_count = len(directories[directory]["opus"])
        flac_count = len(directories[directory]["flac"])
        total = opus_count + flac_count
        rows.append((directory, opus_count, flac_count, total))

    directory_width = max(20, max(len(row[0]) for row in rows))
    border = (
        f"+{'-' * (directory_width + 2)}+------------+------------+-------------+"
    )

    print(border)
    print(
        f"| {'Directory':<{directory_width}} | "
        f"{'Opus Count':>10} | {'FLAC Count':>10} | {'Total Songs':>11} |"
    )
    print(border)

    for directory, opus_count, flac_count, total in rows:
        print(
            f"| {directory:<{directory_width}} | {opus_count:>10} | "
            f"{flac_count:>10} | {total:>11} |"
        )

    print(border)

    total_songs = sum(row[3] for row in rows)
    print(f"\n  Total songs: {total_songs}")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
