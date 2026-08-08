"""
Report how many songs each artist appears on.
Read-only — does not modify any files.
"""

from collections import Counter

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report song count per artist"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def run():
    artists = Counter()
    files = [
        file for file in ROOT.rglob("*")
        if file.is_file() and file.suffix.lower() in READERS
    ]

    print("\n" + "=" * 58)
    print("  ARTIST FREQUENCY REPORT")
    print("=" * 58)
    print(f"  Scanning {len(files):,} FLAC/Opus file(s)...")
    print("-" * 58)

    for index, file in enumerate(files, 1):
        try:
            tags = READERS[file.suffix.lower()](file)

            for field in tags.get("artist", []):
                for artist in field.replace("&", ";").split(";"):
                    artist = artist.strip()
                    if artist:
                        artists[artist] += 1

        except Exception:
            pass

        if index % 500 == 0 or index == len(files):
            print(f"  Progress: {index:>5}/{len(files)}")

    print("\n" + "-" * 58)

    if not artists:
        print("  No artist tags found.")
    else:
        print(f"  {'Songs':>5}  Artist")
        print("  " + "-" * 52)
        for artist, count in artists.most_common():
            print(f"  {count:>5}  {artist}")

    print("\n" + "=" * 58)
    print(f"  {len(artists):,} unique artist(s) found.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
