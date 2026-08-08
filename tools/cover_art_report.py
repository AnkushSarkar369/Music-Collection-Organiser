"""
Analyzes embedded album art across the library: sizes, resolutions,
largest/smallest, top 10 by file size.
Read-only — does not modify any files.
"""

import base64

from mutagen.flac import FLAC, Picture
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Report embedded album art sizes and resolutions"


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
                if not audio.pictures:
                    continue
                pic = audio.pictures[0]
            else:
                audio = OggOpus(file)
                if "metadata_block_picture" not in audio:
                    continue
                pic = Picture(base64.b64decode(audio["metadata_block_picture"][0]))

            size = len(pic.data)
            width = pic.width
            height = pic.height
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

        except Exception:
            pass

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
