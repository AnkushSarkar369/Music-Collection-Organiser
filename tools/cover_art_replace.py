"""Replace low-resolution FLAC artwork using exact-match JPGs from ~/Music/Album Art.

Read-only by default. Use --apply to modify files.
A source JPG is deleted only after the FLAC has been saved and re-opened
successfully with matching embedded image dimensions.
"""

from __future__ import annotations

import argparse
import mimetypes
from io import BytesIO
from pathlib import Path

from PIL import Image
from mutagen.flac import FLAC, Picture

from config import ROOT

DESCRIPTION = "Replace low-resolution FLAC artwork"
ART_ROOT = Path.home() / "Music" / "Album Art"
MIN_DIMENSION = 1000


def image_dimensions(data: bytes) -> tuple[int, int]:
    with Image.open(BytesIO(data)) as image:
        return image.width, image.height


def representative_cover(audio: FLAC):
    if not audio.pictures:
        return None

    inspected = []
    for picture in audio.pictures:
        width, height = image_dimensions(picture.data)
        inspected.append((picture, width, height))

    front_covers = [item for item in inspected if item[0].type == 3]
    candidates = front_covers or inspected
    return max(candidates, key=lambda item: item[1] * item[2])


def replace_cover(flac_path: Path, image_path: Path) -> tuple[int, int, int, int]:
    source_data = image_path.read_bytes()
    source_width, source_height = image_dimensions(source_data)

    if source_width < MIN_DIMENSION and source_height < MIN_DIMENSION:
        raise RuntimeError(
            f"replacement is also low resolution: "
            f"{source_width}×{source_height}"
        )

    audio = FLAC(flac_path)
    current = representative_cover(audio)
    if current is None:
        raise RuntimeError("FLAC has no artwork")

    old_width, old_height = current[1], current[2]

    picture = Picture()
    picture.type = 3
    picture.mime = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    picture.desc = "Cover"
    picture.data = source_data

    audio.clear_pictures()
    audio.add_picture(picture)
    audio.save()

    verified = FLAC(flac_path)
    if not verified.pictures:
        raise RuntimeError("verification failed: no embedded artwork")

    embedded_width, embedded_height = image_dimensions(
        verified.pictures[0].data
    )

    if (embedded_width, embedded_height) != (source_width, source_height):
        raise RuntimeError(
            "verification failed: "
            f"embedded {embedded_width}×{embedded_height}, "
            f"source {source_width}×{source_height}"
        )

    return old_width, old_height, source_width, source_height


def run(apply: bool = False):
    if not ART_ROOT.is_dir():
        raise RuntimeError(f"Album Art folder doesn't exist: {ART_ROOT}")

    candidates = []
    skipped = []
    failed = []
    replaced = []

    for flac_path in sorted(ROOT.rglob("*.flac"), key=lambda p: str(p).casefold()):
        try:
            audio = FLAC(flac_path)
            cover = representative_cover(audio)

            if cover is None:
                continue

            width, height = cover[1], cover[2]
            if width >= MIN_DIMENSION or height >= MIN_DIMENSION:
                continue

            image_path = ART_ROOT / f"{flac_path.stem}.jpg"
            candidates.append((flac_path, image_path, width, height))

        except Exception as exc:
            failed.append((flac_path, f"could not inspect artwork: {exc}"))

    print("\n" + "=" * 72)
    print("  ARTWORK · REPLACE LOW-RESOLUTION COVERS")
    print("=" * 72)
    print(f"  Library   : {ROOT}")
    print(f"  Artwork   : {ART_ROOT}")
    print(f"  Criterion : width < {MIN_DIMENSION} AND height < {MIN_DIMENSION}")
    print(f"  Mode      : {'APPLY' if apply else 'DRY RUN'}")
    print("=" * 72)

    for flac_path, image_path, old_width, old_height in candidates:
        relative = flac_path.relative_to(ROOT)

        if not image_path.is_file():
            skipped.append((flac_path, "exact replacement JPG not found"))
            print(f"  SKIP  {relative} — {image_path.name} not found")
            continue

        try:
            source_data = image_path.read_bytes()
            source_width, source_height = image_dimensions(source_data)

            if source_width < MIN_DIMENSION and source_height < MIN_DIMENSION:
                skipped.append(
                    (flac_path, f"replacement is {source_width}×{source_height}")
                )
                print(
                    f"  SKIP  {relative} — replacement is "
                    f"{source_width}×{source_height}"
                )
                continue

            if not apply:
                print(
                    f"  PLAN  {relative}: "
                    f"{old_width}×{old_height} → "
                    f"{source_width}×{source_height} "
                    f"using {image_path.name}"
                )
                continue

            new_sizes = replace_cover(flac_path, image_path)
            image_path.unlink()
            replaced.append((flac_path, *new_sizes))
            print(
                f"  DONE  {relative}: "
                f"{new_sizes[0]}×{new_sizes[1]} → "
                f"{new_sizes[2]}×{new_sizes[3]}"
            )

        except Exception as exc:
            failed.append((flac_path, str(exc)))
            print(f"  FAIL  {relative} — {exc}")

    print("\n" + "-" * 72)
    print(f"  Low-resolution candidates : {len(candidates):,}")

    if apply:
        print(f"  Replaced                  : {len(replaced):,}")
    else:
        print(f"  Planned                   : {len(candidates) - len(skipped):,}")
        print("  No files were modified.")
        print("  Run with --apply to perform the replacements.")

    print(f"  Skipped                   : {len(skipped):,}")
    print(f"  Failed                    : {len(failed):,}")

    if failed:
        print("\n  FAILURES")
        for file, reason in failed:
            print(f"  - {file.relative_to(ROOT)}: {reason}")

    if skipped:
        print("\n  SKIPPED")
        for file, reason in skipped:
            print(f"  - {file.relative_to(ROOT)}: {reason}")

    print("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform replacements and delete each source JPG after verification",
    )
    args = parser.parse_args()
    run(apply=args.apply)


if __name__ == "__main__":
    main()
