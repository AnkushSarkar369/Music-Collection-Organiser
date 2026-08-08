"""
Scans the library and reports how many songs each artist appears on.
Read-only — does not modify any files.
"""

from collections import Counter
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report song count per artist"


def run():
    artists = Counter()
    files = list(ROOT.rglob("*.flac")) + list(ROOT.rglob("*.opus"))

    print(f"Scanning {len(files)} files...")

    for i, f in enumerate(files, 1):
        try:
            if f.suffix.lower() == ".flac":
                tags = FLAC(f)
            else:
                tags = OggOpus(f)

            for field in tags.get("artist", []):
                for artist in map(str.strip, field.split("&")):
                    if artist:
                        artists[artist] += 1

        except Exception:
            pass

        if i % 500 == 0 or i == len(files):
            print(f"{i}/{len(files)}")

    print("\nArtist counts:\n")
    for artist, count in artists.most_common():
        print(f"{count:4}  {artist}")


if __name__ == "__main__":
    run()