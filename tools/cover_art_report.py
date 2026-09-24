"""
Analyzes embedded album art across the library: sizes, resolutions,
largest/smallest, top 10 by file size.
Read-only — does not modify any files.
"""

import base64
from io import BytesIO

from PIL import Image
from mutagen.flac import FLAC, Picture
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report embedded album art sizes and resolutions"


def get_dimensions(picture):
    """Return reliable image dimensions, falling back to the image bytes."""
    if picture.width > 0 and picture.height > 0:
        return picture.width, picture.height

    with Image.open(BytesIO(picture.data)) as image:
        return image.width, image.height


def run():
    total_bytes = 0
    cover_count = 0

    largest = None
    smallest = None
    highest_dim = None
    lowest_dim = None
    covers = []

    print("\n" + "=" * 58)
    print("  EMBEDDED COVER ART REPORT")
    print("=" * 58)
    print(f"  Scanning: {ROOT}")
    print("-" * 58)

    for file in ROOT.rglob("*"):
        if file.suffix.lower() not in (".flac", ".opus"):
            continue

        try:
            if file.suffix.lower() == ".flac":
                audio = FLAC(file)
                pictures = audio.pictures
            else:
                audio = OggOpus(file)
                values = audio.get("metadata_block_picture", [])
                pictures = [
                    Picture(base64.b64decode(value))
                    for value in values
                ]

            if not pictures:
                continue

            # Prefer an explicitly tagged front cover. If none exists,
            # use the highest-resolution embedded picture.
            front_covers = [picture for picture in pictures if picture.type == 3]
            candidates = front_covers or pictures

            pic = max(
                candidates,
                key=lambda picture: get_dimensions(picture)[0] * get_dimensions(picture)[1],
            )

            size = len(pic.data)
            width, height = get_dimensions(pic)
            pixels = width * height

            total_bytes += size
            cover_count += 1

            info = {
                "file": str(file.relative_to(ROOT)),
                "size": size,
                "width": width,
                "height": height,
                "pixels": pixels,
            }

            covers.append(info)

            if largest is None or size > largest["size"]:
                largest = info
            if smallest is None or size < smallest["size"]:
                smallest = info
            if highest_dim is None or pixels > highest_dim["pixels"]:
                highest_dim = info
            if lowest_dim is None or pixels < lowest_dim["pixels"]:
                lowest_dim = info

        except Exception as e:
            print(f"  [!] Could not inspect {file.relative_to(ROOT)}: {e}")

    if cover_count == 0:
        print("  No embedded covers found.")
        print("=" * 58 + "\n")
        return

    covers.sort(key=lambda x: x["size"], reverse=True)

    avg_w = sum(x["width"] for x in covers) / cover_count
    avg_h = sum(x["height"] for x in covers) / cover_count

    print(f"  Covers found       : {cover_count}")
    print(f"  Total cover size   : {total_bytes / (1024 * 1024):.2f} MB")
    print(f"  Average cover size : {(total_bytes / cover_count) / 1024:.1f} KB")
    print(f"  Average dimension  : {avg_w:.0f} × {avg_h:.0f}")

    print("\n" + "-" * 58)
    print("  LARGEST COVER")
    print("-" * 58)
    print(f"  Size       : {largest['size'] / 1024:.1f} KB")
    print(f"  Resolution : {largest['width']} × {largest['height']}")
    print(f"  File       : {largest['file']}")

    print("\n" + "-" * 58)
    print("  SMALLEST COVER")
    print("-" * 58)
    print(f"  Size       : {smallest['size'] / 1024:.1f} KB")
    print(f"  Resolution : {smallest['width']} × {smallest['height']}")
    print(f"  File       : {smallest['file']}")

    print("\n" + "-" * 58)
    print("  HIGHEST RESOLUTION")
    print("-" * 58)
    print(f"  Resolution : {highest_dim['width']} × {highest_dim['height']}")
    print(f"  Size       : {highest_dim['size'] / 1024:.1f} KB")
    print(f"  File       : {highest_dim['file']}")

    print("\n" + "-" * 58)
    print("  LOWEST RESOLUTION")
    print("-" * 58)
    print(f"  Resolution : {lowest_dim['width']} × {lowest_dim['height']}")
    print(f"  Size       : {lowest_dim['size'] / 1024:.1f} KB")
    print(f"  File       : {lowest_dim['file']}")

    print("\n" + "-" * 58)
    print("  TOP 10 LARGEST COVERS")
    print("-" * 58)
    for i, cover in enumerate(covers[:10], 1):
        print(
            f"  {i:>2}. {cover['size'] / 1024:>8.1f} KB | "
            f"{cover['width']} × {cover['height']} | {cover['file']}"
        )

    print("\n" + "=" * 58)
    print("  Report complete.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
