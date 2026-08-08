"""
Report composers found in the music library.
Read-only — does not modify any files.
"""

from collections import Counter, defaultdict

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report composers and their songs"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def run():
    composers = Counter()
    songs = defaultdict(list)
    checked = 0

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in READERS:
            continue

        checked += 1

        try:
            audio = READERS[file.suffix.lower()](file)
            values = audio.get("composer", [])

            for composer in values:
                composer = composer.strip()
                if not composer:
                    continue

                composers[composer] += 1
                songs[composer].append(file)
        except Exception as e:
            print(f"  [!] Could not inspect {file.relative_to(ROOT)}: {e}")

    print("\n" + "=" * 64)
    print("  COMPOSER REPORT")
    print("=" * 64)
    print(f"  Audio files checked : {checked:,}")
    print(f"  Composers found     : {len(composers):,}")
    print("=" * 64 + "\n")

    if not composers:
        print("  No composer metadata found.\n")
        return

    for composer in sorted(composers, key=str.casefold):
        count = composers[composer]
        print(f"{composer} - {count}")

        for file in sorted(songs[composer], key=lambda f: str(f).casefold()):
            print(f"  {file.relative_to(ROOT)}")

        print()

    print("=" * 64 + "\n")


if __name__ == "__main__":
    run()
