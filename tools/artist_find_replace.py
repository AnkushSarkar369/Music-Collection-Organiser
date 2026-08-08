"""
Find and replace a specific artist name across the library.
Read-only unless a matching artist is found and replaced.
"""

from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus

from config import ROOT

DESCRIPTION = "Find and replace a specific artist name across the library"

READERS = {
    ".flac": FLAC,
    ".opus": OggOpus,
}


def run():
    search = input("Artist name to search: ").strip()
    replace = input("Replace with: ").strip()

    if not search:
        print("\n  [!] Search artist cannot be empty.\n")
        return

    changed = []
    files = [
        file for file in ROOT.rglob("*")
        if file.is_file() and file.suffix.lower() in READERS
    ]

    print("\n" + "=" * 58)
    print("  ARTIST FIND & REPLACE")
    print("=" * 58)
    print(f"  Search : {search}")
    print(f"  Replace: {replace}")
    print(f"  Files  : {len(files):,}")
    print("-" * 58)

    for file in files:
        ext = file.suffix.lower()

        try:
            audio = READERS[ext](file)
            artist_fields = audio.get("artist", [])
            if not artist_fields:
                continue

            modified = False
            new_fields = []

            for field in artist_fields:
                artists = [a.strip() for a in field.replace("&", ";").split(";")]
                new_artists = []

                for artist in artists:
                    if artist.lower() == search.lower():
                        new_artists.append(replace)
                        modified = True
                    else:
                        new_artists.append(artist)

                new_fields.append("; ".join(new_artists))

            if modified:
                old_value = " | ".join(artist_fields)
                audio["artist"] = new_fields
                audio.save()
                new_value = " | ".join(new_fields)
                changed.append((file, old_value, new_value))

        except Exception as e:
            print(f"  [!] Skipped {file.relative_to(ROOT)}: {e}")

    print("\n" + "-" * 58)

    if not changed:
        print("  No files were changed.")
    else:
        print(f"  Changed {len(changed):,} file(s):\n")
        for i, (file, old_artist, new_artist) in enumerate(changed, 1):
            print(f"  {i:03d}. {file.relative_to(ROOT)}")
            print(f"       Before: {old_artist}")
            print(f"       After : {new_artist}")
            print()

    print("=" * 58)
    print("  Done.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    run()
