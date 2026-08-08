"""
Report audio files with no embedded album artwork.
Read-only — does not modify any files.
"""

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report files missing embedded album artwork"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def has_cover(file):
    audio = READERS[file.suffix.lower()](file)

    if file.suffix.lower() == ".flac":
        return bool(audio.pictures)

    return "metadata_block_picture" in audio and bool(audio["metadata_block_picture"])


def run():
    missing = []
    checked = 0

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in READERS:
            continue

        checked += 1

        try:
            if not has_cover(file):
                missing.append(file)
        except Exception as e:
            print(f"  [!] Could not inspect {file.relative_to(ROOT)}: {e}")

    print("\n" + "=" * 64)
    print("  MISSING COVER ART")
    print("=" * 64)
    print(f"  Audio files checked : {checked:,}")
    print(f"  Missing artwork     : {len(missing):,}")
    print("-" * 64)

    if not missing:
        print("  No files are missing embedded album artwork.")
    else:
        for i, file in enumerate(sorted(missing, key=lambda f: str(f).casefold()), 1):
            print(f"  {i:03d}. {file.relative_to(ROOT)}")

    print("=" * 64 + "\n")


if __name__ == "__main__":
    run()
