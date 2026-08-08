"""
List songs by directory.
Read-only — does not modify any files.
"""

from collections import defaultdict

from config import ROOT

DESCRIPTION = "List library songs by directory"

AUDIO_EXTENSIONS = {".flac", ".opus"}


def collect_files():
    directories = defaultdict(list)

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in AUDIO_EXTENSIONS:
            continue

        relative = file.relative_to(ROOT)
        directory = " - ".join(relative.parts[:-1])
        directories[directory].append(file.stem)

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
        songs = sorted(directories[directory], key=str.casefold)
        print(f"{directory} - {len(songs)}")

        for song in songs:
            print(f"  {song}")

        print()

    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
