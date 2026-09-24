"""Replace or embed artwork in FLAC and Opus files.

Dry-run by default. Use --apply to modify files.

Artwork sources are restricted to exact filename matches in ~/Music/Album Art.
The source image is never modified or deleted.
"""

from __future__ import annotations

import argparse
import base64
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

    if path.suffix.lower() == ".flac":
        audio.clear_pictures()
        audio.add_picture(picture)
    else:
        # Ogg Opus stores FLAC Picture blocks in the
        # METADATA_BLOCK_PICTURE Vorbis comment.
        audio["metadata_block_picture"] = [
            base64.b64encode(picture.write()).decode("ascii")
        ]

    audio.save()


# ---------------------------------------------------------------------------
# Artwork-source discovery
# ---------------------------------------------------------------------------

def album_art_candidates(stem: str) -> list[Path]:
    matches = []

    for path in ART_ROOT.iterdir():
        if (
            path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
            and path.stem.casefold() == stem.casefold()
        ):
            matches.append(path)

    return sorted(matches, key=lambda p: p.name.casefold())


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


def pictures_from_audio(audio):
    if isinstance(audio, FLAC):
        return list(audio.pictures)

    encoded = audio.get("metadata_block_picture", [])
    pictures = []

    for value in encoded:
        try:
            pictures.append(Picture(base64.b64decode(value)))
        except Exception:
            continue

    return pictures


def front_cover(audio):
    pictures = pictures_from_audio(audio)

    if not pictures:
        return None

    fronts = [picture for picture in pictures if picture.type == 3]
    return max(fronts or pictures, key=lambda p: p.width * p.height)


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
        image = image_matches[0]
        return image, picture_from_image(image)

    if len(image_matches) > 1:
        return image_matches, None

    return None, None


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
    ambiguous = []
    changed = []
    failed = []
    unmatched = 0

    print("\n" + "=" * 72)
    print("  ARTWORK · REPLACE / EMBED")
    print("=" * 72)
    print(f"  Library : {ROOT}")
    print(f"  Artwork : {ART_ROOT}")
    print("  Source  : matching image from Album Art only")
    print(f"  Mode    : {'APPLY' if apply else 'DRY RUN'}")
    print("=" * 72)

    for target in targets:
        relative = target.relative_to(ROOT)

        try:
            source, picture = source_for(target)

            if source is None:
                unmatched += 1
                continue

            if picture is None:
                ambiguous.append((target, source))
                print(
                    f"  AMBIGUOUS  {relative} — "
                    + ", ".join(path.name for path in source)
                )
                continue

            width, height = picture.width, picture.height

            if not apply:
                planned.append(target)
                print(
                    f"  PLAN  {relative}: "
                    f"{width}×{height} from Album Art ({source.name})"
                )
                continue

            write_picture(target, picture)
            verified_width, verified_height = verify(target, picture)

            changed.append(target)
            print(
                f"  DONE  {relative}: "
                f"{verified_width}×{verified_height} from Album Art ({source.name})"
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

    print(f"  No artwork match     : {unmatched:,}")
    print(f"  Ambiguous matches    : {len(ambiguous):,}")
    print(f"  Failed               : {len(failed):,}")

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
