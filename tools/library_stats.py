"""
Display a compact snapshot of the music library.
Read-only — does not modify any files.
"""

from collections import Counter

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Display a snapshot of the music library"

AUDIO_EXTENSIONS = {".flac", ".opus"}
READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def run():
    song_count = Counter()
    artists = set()
    directories = set()
    total_bytes = 0
    files = []

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in AUDIO_EXTENSIONS:
            continue

        ext = file.suffix.lower()
        files.append(file)
        song_count[ext] += 1
        total_bytes += file.stat().st_size

        relative = file.relative_to(ROOT)
        directories.add(relative.parent)

        try:
            audio = READERS[ext](file)
            for field in audio.get("artist", []):
                for artist in field.split(";"):
                    artist = artist.strip()
                    if artist:
                        artists.add(artist)
        except Exception:
            pass

    flac_count = song_count[".flac"]
    opus_count = song_count[".opus"]
    total_songs = flac_count + opus_count
    size_gb = total_bytes / (1024 ** 3)

    width = 48

    print("\n" + "=" * width)
    print("  MUSIC LIBRARY SNAPSHOT")
    print("=" * width)
    print(f"  Library       : {ROOT}")
    print("-" * width)
    print(f"  Total songs   : {total_songs:,}")
    print(f"  FLAC          : {flac_count:,}")
    print(f"  Opus          : {opus_count:,}")
    print(f"  Artists       : {len(artists):,}")
    print(f"  Directories   : {len(directories):,}")
    print(f"  Library size  : {size_gb:,.2f} GB")
    print("=" * width + "\n")


if __name__ == "__main__":
    run()
