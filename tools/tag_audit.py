"""Audit core music metadata for unexpected or non-canonical tags.
Read-only — does not modify any files.
"""

from collections import Counter

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Audit music tags for missing, extra, and non-canonical metadata"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}

EXPECTED_TAGS = {"artist", "album", "composer"}
IGNORED_INTERNAL_KEYS = {"metadata_block_picture"}


def run():
    missing = Counter()
    extra = Counter()
    comma_artists = []
    unsorted_artists = []
    checked = 0
    errors = 0

    for file in sorted(ROOT.rglob("*"), key=lambda p: str(p).casefold()):
        extension = file.suffix.lower()
        if not file.is_file() or extension not in READERS:
            continue

        checked += 1

        try:
            audio = READERS[extension](file)
            keys = {key.casefold() for key in audio.keys()}

            for field in EXPECTED_TAGS:
                if not audio.get(field, []):
                    missing[field] += 1

            for key in keys - EXPECTED_TAGS - IGNORED_INTERNAL_KEYS:
                extra[key] += 1

            for artist in audio.get("artist", []):
                if "," in artist:
                    comma_artists.append((file, artist))

                parts = [part.strip() for part in artist.split(";") if part.strip()]
                if len(parts) > 1 and parts != sorted(parts, key=str.casefold):
                    unsorted_artists.append(
                        (file, artist, "; ".join(sorted(parts, key=str.casefold)))
                    )

        except Exception as e:
            errors += 1
            print(f"  [!] Could not inspect {file.relative_to(ROOT)}: {e}")

    print("\n" + "=" * 72)
    print("  TAG AUDIT")
    print("=" * 72)
    print(f"  Audio files checked : {checked:,}")
    print(f"  Errors              : {errors:,}")
    print("=" * 72)

    print("\n  MISSING EXPECTED TAGS")
    print("  " + "-" * 68)
    for field in sorted(EXPECTED_TAGS):
        print(f"  {field:<12} {missing[field]:,} files")

    print("\n  EXTRA TAGS")
    print("  " + "-" * 68)
    if not extra:
        print("  None")
    else:
        for key, count in sorted(extra.items()):
            print(f"  {key:<24} {count:,} files")

    print("\n  ARTIST FIELDS CONTAINING COMMAS")
    print("  " + "-" * 68)
    if not comma_artists:
        print("  None")
    else:
        for file, artist in comma_artists:
            print(f"  {file.relative_to(ROOT)}")
            print(f"    {artist}")

    print("\n  ARTIST FIELDS NOT ALPHABETICALLY SORTED")
    print("  " + "-" * 68)
    if not unsorted_artists:
        print("  None")
    else:
        for file, artist, expected in unsorted_artists:
            print(f"  {file.relative_to(ROOT)}")
            print(f"    Current : {artist}")
            print(f"    Expected: {expected}")

    print("\n" + "=" * 72 + "\n")


if __name__ == "__main__":
    run()
