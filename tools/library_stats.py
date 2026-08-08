"""
Display detailed statistics for the music library.
Read-only — does not modify any files.
"""

import base64
import re
from collections import defaultdict

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Display detailed statistics for the music library"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}
AUDIO_EXTENSIONS = set(READERS)
ARTIST_SEPARATOR_PATTERN = re.compile(
    r"\s*(?:;|&|\bfeat\.?\b|\bfeaturing\b|\bft\.?\b)\s*",
    flags=re.IGNORECASE,
)


def artwork_size(audio, extension):
    if extension == ".flac":
        return sum(len(picture.data) for picture in audio.pictures)

    total = 0
    for value in audio.get("metadata_block_picture", []):
        try:
            total += len(base64.b64decode(value))
        except Exception:
            pass
    return total


def format_size(size):
    if size >= 1024 ** 3:
        return f"{size / (1024 ** 3):.2f} GB"
    if size >= 1024 ** 2:
        return f"{size / (1024 ** 2):.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size:,} B"


def split_artists(value):
    return [artist.strip() for artist in ARTIST_SEPARATOR_PATTERN.split(value) if artist.strip()]


def run():
    directories = defaultdict(
        lambda: {
            "flac": 0,
            "flac_size": 0,
            "opus": 0,
            "opus_size": 0,
            "artwork_size": 0,
            "artists": set(),
        }
    )

    total_size = 0
    total_artists = set()

    for file in ROOT.rglob("*"):
        extension = file.suffix.lower()
        if not file.is_file() or extension not in AUDIO_EXTENSIONS:
            continue

        relative = file.relative_to(ROOT)
        directory = " - ".join(relative.parts[:-1])
        data = directories[directory]
        file_size = file.stat().st_size
        total_size += file_size

        if extension == ".flac":
            data["flac"] += 1
            data["flac_size"] += file_size
        else:
            data["opus"] += 1
            data["opus_size"] += file_size

        try:
            audio = READERS[extension](file)

            for field in audio.get("artist", []):
                for artist in split_artists(field):
                    data["artists"].add(artist)
                    total_artists.add(artist)

            artwork = artwork_size(audio, extension)
            data["artwork_size"] += artwork
        except Exception:
            pass

    if not directories:
        print("\n" + "=" * 72)
        print("  LIBRARY STATISTICS")
        print("=" * 72)
        print("  No FLAC or Opus files found.")
        print("=" * 72 + "\n")
        return

    rows = []
    for directory in sorted(directories, key=str.casefold):
        data = directories[directory]
        rows.append(
            (
                directory,
                data["flac"],
                data["flac_size"],
                data["opus"],
                data["opus_size"],
                data["artwork_size"],
                len(data["artists"]),
            )
        )

    directory_width = max(20, max(len(row[0]) for row in rows))
    border = (
        f"+{'-' * (directory_width + 2)}+-------+------------+-------+------------+---------------+---------+"
    )

    print("\n" + "=" * (len(border) - 1))
    print("  LIBRARY STATISTICS")
    print("=" * (len(border) - 1))
    print(f"  Library: {ROOT}")
    print()
    print(border)
    print(
        f"| {'Directory':<{directory_width}} | {'FLAC':>5} | {'FLAC Size':>10} | "
        f"{'Opus':>5} | {'Opus Size':>10} | {'Artwork Size':>13} | {'Artists':>7} |"
    )
    print(border)

    for directory, flac, flac_size, opus, opus_size, artwork, artists in rows:
        print(
            f"| {directory:<{directory_width}} | {flac:>5} | {format_size(flac_size):>10} | "
            f"{opus:>5} | {format_size(opus_size):>10} | {format_size(artwork):>13} | {artists:>7} |"
        )

    print(border)

    flac_count = sum(row[1] for row in rows)
    opus_count = sum(row[3] for row in rows)
    total_songs = flac_count + opus_count

    print()
    print("=" * 48)
    print("  MUSIC LIBRARY SNAPSHOT")
    print("=" * 48)
    print("-" * 48)
    print(f"  Total songs   : {total_songs:,}")
    print(f"  FLAC          : {flac_count:,}")
    print(f"  Opus          : {opus_count:,}")
    print(f"  Artists       : {len(total_artists):,}")
    print(f"  Directories   : {len(rows):,}")
    print(f"  Library size  : {format_size(total_size)}")
    print("=" * 48 + "\n")


if __name__ == "__main__":
    run()
