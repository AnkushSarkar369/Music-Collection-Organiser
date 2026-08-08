"""
Master menu for flac-library-tools.
Run this from the project root: python3 master.py
"""

from tools import (
    artist_find_replace,
    artist_frequency_report,
    artist_standardize,
    bracket_tag_report,
    cover_art_report,
)


TOOLS = [
    ("Find & replace specific artist name.", artist_find_replace.run),
    ("Report song count per artist", artist_frequency_report.run),
    ("Standardize artist names (separators + rename map + alphabetize)", artist_standardize.run),
    ("Report bracketed tags found in filenames", bracket_tag_report.run),
    ("Report embedded album art sizes and resolutions", cover_art_report.run),
]


def main():
    while True:
        print("\n" + "=" * 50)
        print("flac-library-tools")
        print("=" * 50)

        for i, (description, _) in enumerate(TOOLS, 1):
            print(f"{i}. {description}")

        print("0. Exit")

        choice = input("\nPick: ").strip()

        if choice == "0":
            break

        try:
            option = int(choice)
            if option < 1 or option > len(TOOLS):
                raise ValueError
        except ValueError:
            print("Invalid choice.")
            continue

        print()
        try:
            TOOLS[option - 1][1]()
        except KeyboardInterrupt:
            print("\nInterrupted.")
        except Exception as e:
            print(f"Tool crashed: {e}")


if __name__ == "__main__":
    main()
