"""
Standardizes artist tags:

1. Normalizes artist separators to ';'
2. Applies fixed rename map (typos, preferred spellings)
3. Alphabetizes multi-artist fields
4. Uses "; " as the only canonical separator

Interactive:
    y = apply
    n = skip
    a = accept all remaining
    q = quit
"""

import re

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Standardize artist names (separators + rename map + alphabetize)"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


ARTIST_MAP = {
    "mohdrafi": "Mohammed Rafi",
    "arrahman": "Allah Rakha Rahman",
    "rdburman": "Rahul Dev Burman",
    "hemantkumar": "Hemanta Mukhopadhyay",
    "hemantamukherjee": "Hemanta Mukhopadhyay",
    "hemantamukherji": "Hemanta Mukhopadhyay",
    "hemantmukherjee": "Hemanta Mukhopadhyay",
    "hemantmukherji": "Hemanta Mukhopadhyay",
    "shankarehsaanloy": "Shankar-Ehsaan-Loy",
    "kalyanjianandji": "Kalyanji-Anandji",
}


# These are the only supported artist separators:
# ;, &, feat, feat., ft, ft., featuring
SEPARATOR_PATTERN = re.compile(
    r"\s*(?:;|&|\bfeat\.?\b|\bfeaturing\b|\bft\.?\b)\s*",
    flags=re.IGNORECASE,
)


def artist_key(text: str) -> str:
    """Create a comparison key that ignores case, spaces, and punctuation."""
    return re.sub(r"[^a-z0-9]", "", text.casefold())


def normalize_separators(text: str) -> str:
    """Normalize supported artist separators to ';'."""
    if not text:
        return ""

    text = SEPARATOR_PATTERN.sub(";", text)
    text = re.sub(r"\s*;\s*", ";", text)
    text = re.sub(r";{2,}", ";", text)
    text = text.strip("; ")
    text = " ".join(text.split())

    return text


def standardize(text: str) -> str:
    """Return the canonical artist string: 'Artist A; Artist B; Artist C'."""
    text = normalize_separators(text)

    if not text:
        return ""

    artists = [artist.strip() for artist in text.split(";") if artist.strip()]
    artists = [ARTIST_MAP.get(artist_key(artist), artist) for artist in artists]
    artists = sorted(artists, key=str.casefold)

    return "; ".join(artists)


def run():
    auto_accept = False
    updated = 0
    skipped = 0

    print("\n" + "=" * 58)
    print("  ARTIST STANDARDIZATION")
    print("=" * 58)
    print(f"  Library: {ROOT}")
    print("  Canonical format: Artist A; Artist B; Artist C")
    print("-" * 58)
    print("  Commands: y = apply | n = skip | a = accept all | q = quit")
    print("=" * 58 + "\n")

    for file in ROOT.rglob("*"):
        ext = file.suffix.lower()

        if ext not in READERS:
            continue

        try:
            audio = READERS[ext](file)
            artist_fields = audio.get("artist", [])

            if not artist_fields:
                continue

            before = artist_fields[0]
            after = standardize(before)

            if before == after:
                continue

            if not auto_accept:
                print("-" * 58)
                print(f"  File   : {file.relative_to(ROOT)}")
                print(f"  Before : {before}")
                print(f"  After  : {after}")
                print("-" * 58)

                choice = input("  Apply change? [y/n/a/q]: ").strip().lower()

                if choice == "q":
                    print("\n  Operation cancelled by user.")
                    break

                if choice == "n":
                    skipped += 1
                    continue

                if choice == "a":
                    auto_accept = True

                if choice not in ("y", "a"):
                    skipped += 1
                    continue

            audio["artist"] = after
            audio.save()
            updated += 1

            if auto_accept:
                print(f"  Applied: {before} -> {after}")
            else:
                print("  Applied.\n")

        except Exception as e:
            print(f"  [!] {file.name}: {e}")

    print("\n" + "=" * 58)
    print("  STANDARDIZATION COMPLETE")
    print("=" * 58)
    print(f"  Updated : {updated}")
    print(f"  Skipped : {skipped}")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
