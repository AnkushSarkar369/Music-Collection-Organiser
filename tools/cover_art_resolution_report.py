"""
Report embedded album artwork with both dimensions strictly below 1000 pixels.
Read-only — does not modify any files.
"""

import base64

from mutagen.flac import FLAC, Picture
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report embedded artwork below 1000x1000"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def get_picture(file):
    audio = READERS[file.suffix.lower()](file)

    if file.suffix.lower() == ".flac":
        if not audio.pictures:
            return None
        return audio.pictures[0]

    if "metadata_block_picture" not in audio:
        return None

    return Picture(base64.b64decode(audio["metadata_block_picture"][0]))


def run():
    low_resolution = []
    checked = 0

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in READERS:
            continue

        checked += 1

        try:
            picture = get_picture(file)
            if picture is None:
                continue

            if picture.width < 1000 and picture.height < 1000:
                low_resolution.append(
                    (file, picture.width, picture.height)
                )
        except Exception as e:
            print(f"  [!] Could not inspect {file.relative_to(ROOT)}: {e}")

    low_resolution.sort(key=lambda item: str(item[0]).casefold())

    print("\n" + "=" * 72)
    print("  LOW-RESOLUTION COVER ART")
    print("=" * 72)
    print("  Criteria: width < 1000 AND height < 1000")
    print(f"  Audio files checked : {checked:,}")
    print(f"  Files below limit   : {len(low_resolution):,}")
    print("-" * 72)

    if not low_resolution:
        print("  No embedded artwork below 1000×1000 was found.")
    else:
        print(f"  {'Resolution':<14} File")
        print("  " + "-" * 66)
        for file, width, height in low_resolution:
            resolution = f"{width}×{height}"
            print(f"  {resolution:<14} {file.relative_to(ROOT)}")

    print("=" * 72 + "\n")


if __name__ == "__main__":
    run()
