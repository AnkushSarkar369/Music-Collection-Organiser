"""Replace or embed artwork in FLAC and Opus files.

Dry-run by default. Use --apply to modify files.
Artwork source priority:
1. Exact matching image in ~/Music/Album Art
2. Exact matching FLAC/Opus file with embedded artwork

The source audio file and source image are never modified or deleted.
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

DESCRIPTION = "Replace or embed artwork in FLAC and Opus files"
ART_ROOT = Path.home() / "Music" / "Album Art"
AUDIO_EXTENSIONS = {".flac", ".opus"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ---------------------------------------------------------------------------
# File-format handling
# ---------------------------------------------------------------------------

def open_audio(path: Path):
    if path.suffix.lower() == ".flac":
        return FLAC(path)
    if path.suffix.lower() == ".opus":
        return OggOpus(path)
    raise RuntimeError(f"unsupported audio format: {path.suffix}")


def write_picture(path: Path, picture: Picture):
    audio = open_audio(path)
    audio.clear_pictures()
    audio.add_picture(picture)
    audio.save()


# ---------------------------------------------------------------------------
# Artwork-source discovery
# ---------------------------------------------------------------------------

def album_art_candidates(stem: str) -> list[Path]:
    matches = []
    for path in ART_ROOT.iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            if path.stem.casefold() == stem.casefold():
                matches.append(path)
    return sorted(matches, key=lambda p: p.name.casefold())


def audio_candidates(target: Path) -> list[Path]:
    matches = []
    for path in ROOT.rglob("*"):
        if (
            path.is_file()
            and path != target
            and path.suffix.lower() in AUDIO_EXTENSIONS
            and path.stem.casefold() == target.stem.casefold()
        ):
            matches.append(path)
    return sorted(matches, key=lambda p: str(p).casefold())


def front_cover(audio):
    pictures = getattr(audio, "pictures", [])
    if not pictures:
        return None

    fronts = [picture for picture in pictures if picture.type == 3]
    return max(fronts or pictures, key=lambda p: p.width * p.height)


def find_audio_source(target: Path):
    candidates = []

    for path in audio_candidates(target):
        try:
            picture = front_cover(open_audio(path))
            if picture is not None:
                candidates.append((path, picture))
        except Exception:
            continue

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        return candidates

    return None


# ---------------------------------------------------------------------------
# Artwork construction and verification
# ---------------------------------------------------------------------------

def picture_from_image(path: Path) -> Picture:
    data = path.read_bytes()

    with Image.open(BytesIO(data)) as image:
        width, height = image.width, image.height
        depth = len(image.getbands()) * 8

    picture = Picture()
    picture.type = 3
    picture.mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    picture.desc = "Cover"
    picture.width = width
    picture.height = height
    picture.depth = depth
    picture.data = data
    return picture


def verify(path: Path, expected: Picture):
    audio = open_audio(path)
    actual = front_cover(audio)

    if actual is None:
        raise RuntimeError("verification failed: no embedded artwork")

    if actual.data != expected.data:
        raise RuntimeError("verification failed: embedded artwork differs from source")

    return actual.width, actual.height


def source_for(target: Path):
    image_matches = album_art_candidates(target.stem)

    if len(image_matches) == 1:
        return ("Album Art", image_matches[0], picture_from_image(image_matches[0]))

    if len(image_matches) > 1:
        return ("ambiguous Album Art", image_matches, None)

    audio_source = find_audio_source(target)

    if audio_source is None:
        return (None, None, None)

    if isinstance(audio_source, list):
        return ("ambiguous audio source", audio_source, None)

    source_path, picture = audio_source
    return ("matching audio", source_path, picture)


# ---------------------------------------------------------------------------
# Main operation
# ---------------------------------------------------------------------------

def run(apply: bool = False):
    if not ART_ROOT.is_dir():
        raise RuntimeError(f"Album Art folder doesn't exist: {ART_ROOT}")

    targets = sorted(
        (
            path
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
        ),
        key=lambda p: str(p).casefold(),
    )

    planned = []
    changed = []
    skipped = []
    failed = []

    print("\n" + "=" * 72)
    print("  ARTWORK · REPLACE / EMBED")
    print("=" * 72)
    print(f"  Library : {ROOT}")
    print(f"  Artwork : {ART_ROOT}")
    print("  Sources : Album Art → matching audio file artwork")
    print(f"  Mode    : {'APPLY' if apply else 'DRY RUN'}")
    print("=" * 72)

    for target in targets:
        relative = target.relative_to(ROOT)

        try:
            source_kind, source, picture = source_for(target)

            if source_kind is None:
                skipped.append((target, "no matching artwork source"))
                print(f"  SKIP  {relative} — no matching artwork source")
                continue

            if source_kind == "ambiguous Album Art":
                names = ", ".join(path.name for path in source)
                skipped.append((target, f"ambiguous Album Art: {names}"))
                print(f"  SKIP  {relative} — ambiguous Album Art: {names}")
                continue

            if source_kind == "ambiguous audio source":
                names = ", ".join(
                    str(path.relative_to(ROOT)) for path, _ in source
                )
                skipped.append((target, f"ambiguous audio source: {names}"))
                print(f"  SKIP  {relative} — ambiguous audio source")
                continue

            width, height = picture.width, picture.height

            if not apply:
                planned.append(target)
                print(
                    f"  PLAN  {relative}: "
                    f"{width}×{height} from {source_kind} "
                    f"({source.name})"
                )
                continue

            write_picture(target, picture)
            verified_width, verified_height = verify(target, picture)

            changed.append(target)
            print(
                f"  DONE  {relative}: "
                f"{verified_width}×{verified_height} from {source_kind} "
                f"({source.name})"
            )

        except Exception as exc:
            failed.append((target, str(exc)))
            print(f"  FAIL  {relative} — {exc}")

    print("\n" + "-" * 72)
    print(f"  Audio files scanned : {len(targets):,}")

    if apply:
        print(f"  Artwork replaced    : {len(changed):,}")
    else:
        print(f"  Planned              : {len(planned):,}")
        print("  No files were modified.")
        print("  Run with --apply to perform the replacements.")

    print(f"  Skipped              : {len(skipped):,}")
    print(f"  Failed               : {len(failed):,}")

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
    choice = input("Apply the planned artwork replacements? [y/N]: ").strip().lower()
    if choice in {"y", "yes"}:
        run(apply=True)
    else:
        print("No files were modified.\n")


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="replace/embed the planned artwork",
    )
    args = parser.parse_args()
    run(apply=args.apply)


if __name__ == "__main__":
    main()
