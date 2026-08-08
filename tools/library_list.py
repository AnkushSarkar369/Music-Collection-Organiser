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

    if not directories:
        print("No FLAC or Opus files found.")
        return

    for directory in sorted(directories, key=str.casefold):
        print(directory)

        songs = directories[directory]["flac"] + directories[directory]["opus"]
        for song in sorted(songs, key=str.casefold):
            print(song)

        print()

    print("+----------------------+------------+------------+-------------+")
    print("| Directory            | Opus Count | FLAC Count | Total Songs |")
    print("+----------------------+------------+------------+-------------+")

    for directory in sorted(directories, key=str.casefold):
        opus_count = len(directories[directory]["opus"])
        flac_count = len(directories[directory]["flac"])
        total = opus_count + flac_count

        print(
            f"| {directory:<20} | {opus_count:>10} | "
            f"{flac_count:>10} | {total:>11} |"
        )

    print("+----------------------+------------+------------+-------------+")


if __name__ == "__main__":
    run()
