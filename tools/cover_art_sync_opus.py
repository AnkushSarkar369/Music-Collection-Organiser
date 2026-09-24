"""Embed artwork into Opus files from Album Art or matching FLAC files.

Dry-run by default. Use --apply to write artwork into Opus files.
The source artwork is never deleted and FLAC files are never modified.
"""

from __future__ import annotations

import argparse
import mimetypes
from io import BytesIO
from pathlib import Path

from PIL import Image
from mutagen.flac import FLAC, Picture
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Sync Opus artwork from Album Art or matching FLAC files"
ART_ROOT = Path.home() / "Music" / "Album Art"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def image_dimensions(data: bytes) -> tuple[int, int]:
    with Image.open(BytesIO(data)) as image:
        return image.width, image.height


def album_art_candidates(stem: str) -> list[Path]:
    matches = []
    for path in ART_ROOT.iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            if path.stem.casefold() == stem.casefold():
                matches.append(path)
    return sorted(matches, key=lambda p: p.name.casefold())


def flac_candidates(stem: str) -> list[Path]:
    matches = [
        path
        for path in ROOT.rglob("*.flac")
        if path.stem.casefold() == stem.casefold()
    ]
    return sorted(matches, key=lambda p: str(p).casefold())


def picture_from_file(image_path: Path) -> Picture:
    data = image_path.read_bytes()
    width, height = image_dimensions(data)

    picture = Picture()
    picture.type = 3
    picture.mime = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    picture.desc = "Cover"
    picture.width = width
    picture.height = height
    picture.depth = 24
    picture.data = data
    return picture


def picture_from_flac(flac_path: Path):
    audio = FLAC(flac_path)
    if not audio.pictures:
        return None

    front = [picture for picture in audio.pictures if picture.type == 3]
    return max(front or audio.pictures, key=lambda p: p.width * p.height)


def find_source(opus_path: Path):
    art_matches = album_art_candidates(opus_path.stem)
    if len(art_matches) == 1:
        return ("Album Art", art_matches[0], None)

    if len(art_matches) > 1:
        return ("ambiguous Album Art", art_matches, None)

    flac_matches = flac_candidates(opus_path.stem)
    if len(flac_matches) == 1:
        picture = picture_from_flac(flac_matches[0])
        if picture is not None:
            return ("FLAC", flac_matches[0], picture)
        return ("FLAC has no artwork", flac_matches[0], None)

    if len(flac_matches) > 1:
        return ("ambiguous FLAC", flac_matches, None)

    return (None, None, None)


def build_picture(source_kind, source, existing_picture=None):
    if source_kind == "Album Art":
        return picture_from_file(source)

    if source_kind == "FLAC":
        return existing_picture

    raise RuntimeError(f"unsupported source: {source_kind}")


def embed_cover(opus_path: Path, picture: Picture) -> tuple[int, int]:
    audio = OggOpus(opus_path)
    audio.clear_pictures()
    audio.add_picture(picture)
    audio.save()

    verified = OggOpus(opus_path)
    if not verified.pictures:
        raise RuntimeError("verification failed: no embedded artwork")

    embedded = verified.pictures[0]
    width, height = image_dimensions(embedded.data)
    return width, height


def run(apply: bool = False):
    if not ART_ROOT.is_dir():
        raise RuntimeError(f"Album Art folder doesn't exist: {ART_ROOT}")

    opus_files = sorted(
        ROOT.rglob("*.opus"),
        key=lambda p: str(p).casefold(),
    )

    planned = []
    skipped = []
    failed = []
    embedded = []

    print("\n" + "=" * 72)
    print("  ARTWORK · SYNC OPUS COVERS")
    print("=" * 72)
    print(f"  Library   : {ROOT}")
    print(f"  Artwork   : {ART_ROOT}")
    print("  Priority  : Album Art → matching FLAC artwork")
    print(f"  Mode      : {'APPLY' if apply else 'DRY RUN'}")
    print("=" * 72)

    for opus_path in opus_files:
        relative = opus_path.relative_to(ROOT)

        try:
            source_kind, source, flac_picture = find_source(opus_path)

            if source_kind is None:
                skipped.append((opus_path, "no matching Album Art or FLAC"))
                print(f"  SKIP  {relative} — no artwork source found")
                continue

            if source_kind == "ambiguous Album Art":
                names = ", ".join(path.name for path in source)
                skipped.append((opus_path, f"ambiguous Album Art: {names}"))
                print(f"  SKIP  {relative} — ambiguous Album Art: {names}")
                continue

            if source_kind == "ambiguous FLAC":
                names = ", ".join(
                    str(path.relative_to(ROOT)) for path in source
                )
                skipped.append((opus_path, f"ambiguous FLAC: {names}"))
                print(f"  SKIP  {relative} — ambiguous FLAC match")
                continue

            if source_kind == "FLAC has no artwork":
                skipped.append((opus_path, "matching FLAC has no artwork"))
                print(f"  SKIP  {relative} — matching FLAC has no artwork")
                continue

            picture = build_picture(source_kind, source, flac_picture)
            width, height = image_dimensions(picture.data)

            if not apply:
                planned.append(opus_path)
                print(
                    f"  PLAN  {relative}: "
                    f"{width}×{height} from {source_kind} "
                    f"({source.name})"
                )
                continue

            verified_width, verified_height = embed_cover(opus_path, picture)
            embedded.append(opus_path)
            print(
                f"  DONE  {relative}: "
                f"{verified_width}×{verified_height} from {source_kind} "
                f"({source.name})"
            )

        except Exception as exc:
            failed.append((opus_path, str(exc)))
            print(f"  FAIL  {relative} — {exc}")

    print("\n" + "-" * 72)
    print(f"  Opus files scanned : {len(opus_files):,}")

    if apply:
        print(f"  Embedded           : {len(embedded):,}")
    else:
        print(f"  Planned            : {len(planned):,}")
        print("  No files were modified.")
        print("  Run with --apply to embed the covers.")

    print(f"  Skipped            : {len(skipped):,}")
    print(f"  Failed             : {len(failed):,}")

    if skipped:
        print("\n  SKIPPED")
        for file, reason in skipped:
            print(f"  - {file.relative_to(ROOT)}: {reason}")

    if failed:
        print("\n  FAILURES")
        for file, reason in failed:
            print(f"  - {file.relative_to(ROOT)}: {reason}")

    print("=" * 72 + "\n")


def menu():
    run(apply=False)
    choice = input("Apply the planned Opus artwork? [y/N]: ").strip().lower()
    if choice in {"y", "yes"}:
        run(apply=True)
    else:
        print("No files were modified.\n")


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="embed the planned covers into Opus files",
    )
    args = parser.parse_args()
    run(apply=args.apply)


if __name__ == "__main__":
    main()
