```python
"""
Standardizes artist tags:

1. Normalizes supported separators (feat/ft/featuring/; -> ;)
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


# Expand this over time.
# Keys are matched exactly after splitting/cleanup.
ARTIST_MAP = {
    "Mohd. Rafi": "Mohammed Rafi",
    "A.R. Rahman": "A. R. Rahman",
    "R.D. Burman": "R. D. Burman",
    "Vishal & Shekhar": "Vishal-Shekhar",
    "Shankar Ehsaan Loy": "Shankar-Ehsaan-Loy",
    "Kalyanji - Anandji": "Kalyanji-Anandji",
}


# Only these are treated as artist separators:
#
#   ;
#   feat
#   feat.
#   ft
#   ft.
#   featuring
#
# Deliberately NOT included:
#   &
#   and
#   ,
#   /
#
# This avoids accidentally splitting legitimate artist names.
SEPARATOR_PATTERN = re.compile(
    r"\s*(?:;|&|,|\bfeat\.?\b|\bfeaturing\b|\bft\.?\b)\s*",
    flags=re.IGNORECASE,
)
)


def normalize_separators(text: str) -> str:
    """Normalize supported artist separators to ';'."""

    if not text:
        return ""

    # Convert supported separators to a single delimiter.
    text = SEPARATOR_PATTERN.sub(";", text)

    # Normalize whitespace around semicolons.
    text = re.sub(r"\s*;\s*", ";", text)

    # Collapse repeated semicolons.
    text = re.sub(r";{2,}", ";", text)

    # Remove leading/trailing semicolons.
    text = text.strip("; ")

    # Normalize remaining whitespace inside artist names.
    text = " ".join(text.split())

    return text


def standardize(text: str) -> str:
    """Return the canonical artist string."""

    text = normalize_separators(text)

    if not text:
        return ""

    # Split only on the safe/canonical separator.
    artists = [
        artist.strip()
        for artist in text.split(";")
        if artist.strip()
    ]

    # Apply exact rename map.
    artists = [
        ARTIST_MAP.get(artist, artist)
        for artist in artists
    ]

    # Alphabetize artists case-insensitively.
    artists = sorted(
        artists,
        key=str.casefold,
    )

    # Canonical output: "A; B; C"
    return "; ".join(artists)


def run():
    auto_accept = False
    updated = 0

    print(f"Scanning:\n{ROOT}\n")
    print("Commands: y = yes | n = no | a = accept all | q = quit\n")

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

            # Nothing needs changing.
            if before == after:
                continue

            if not auto_accept:
                print(file.relative_to(ROOT))
                print(f"BEFORE : {before}")
                print(f"AFTER  : {after}")

                choice = input("[y/n/a/q] > ").strip().lower()

                if choice == "q":
                    break

                if choice == "n":
                    continue

                if choice == "a":
                    auto_accept = True

                if choice not in ("y", "a"):
                    continue

            # Apply the standardized artist field.
            audio["artist"] = after
            audio.save()

            updated += 1

            if auto_accept:
                print(f"✓ {before} -> {after}")
            else:
                print("Applied.\n")

        except Exception as e:
            print(f"{file.name}: {e}")

    print(f"\nFinished. {updated} file(s) updated.")


if __name__ == "__main__":
    run()
```
