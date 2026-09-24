"""Audit embedded album artwork for missing and low-resolution covers.
Read-only — does not modify any files.
"""

import base64
from io import BytesIO

from PIL import Image
from mutagen.flac import FLAC, Picture
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Audit embedded album artwork"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def get_pictures(file):
    """Return embedded Picture blocks for FLAC and Opus files."""
    extension = file.suffix.lower()
    audio = READERS[extension](file)

    if extension == ".flac":
        return audio.pictures

    values = audio.get("metadata_block_picture", [])
    pictures = []

    for value in values:
        try:
            pictures.append(Picture(base64.b64decode(value)))
        except Exception:
            continue

    return pictures


def inspect_picture(picture):
    """Return actual image dimensions and raw data."""
    with Image.open(BytesIO(picture.data)) as image:
        return {
            "type": picture.type,
            "data": picture.data,
            "width": image.width,
            "height": image.height,
        }


def get_cover(file):
    """Select the representative cover using actual image dimensions."""
    pictures = get_pictures(file)

    if not pictures:
        return None

    inspected = [inspect_picture(picture) for picture in pictures]
    front_covers = [picture for picture in inspected if picture["type"] == 3]
    candidates = front_covers or inspected

    return max(
        candidates,
        key=lambda picture: picture["width"] * picture["height"],
    )


def run():
    missing = []
    low_resolution = []
    checked = 0

    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in READERS:
            continue

        checked += 1

        try:
            picture = get_cover(file)

            if picture is None:
                missing.append(file)
            elif picture["width"] < 1000 and picture["height"] < 1000:
                low_resolution.append(
                    (file, picture["width"], picture["height"])
                )
        except Exception as e:
            print(f"  [!] Could not inspect {file.relative_to(ROOT)}: {e}")

    missing.sort(key=lambda file: str(file).casefold())
    low_resolution.sort(key=lambda item: str(item[0]).casefold())

    issue_count = len(missing) + len(low_resolution)

    print("\n" + "=" * 72)
    print("  ARTWORK AUDIT")
    print("=" * 72)
    print(f"  Audio files checked : {checked:,}")
    print(f"  Issues found        : {issue_count:,}")
    print("=" * 72)

    print("\n  MISSING ARTWORKS")
    print("  " + "-" * 68)

    if not missing:
        print("  None")
    else:
        for index, file in enumerate(missing, 1):
            print(f"  {index:03d}. {file.relative_to(ROOT)}")

    print("\n  LOW RESOLUTION ARTWORKS")
    print("  " + "-" * 68)
    print("  Criteria: width < 1000 AND height < 1000")

    if not low_resolution:
        print("  None")
    else:
        print(f"  {'Resolution':<14} File")
        print("  " + "-" * 66)
        for file, width, height in low_resolution:
            resolution = f"{width}×{height}"
            print(f"  {resolution:<14} {file.relative_to(ROOT)}")

    print("\n" + "=" * 72 + "\n")


if __name__ == "__main__":
    run()
