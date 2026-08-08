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
    library_list,
    library_stats,
)


TOOLS = [
    ("Find & replace specific artist name.", artist_find_replace.run),
    ("Report song count per artist", artist_frequency_report.run),
    ("Standardize artist names (separators + rename map + alphabetize)", artist_standardize.run),
    ("Report bracketed tags found in filenames", bracket_tag_report.run),
    ("Report embedded album art sizes and resolutions", cover_art_report.run),
    ("List library songs by directory", library_list.run),
    ("Display a snapshot of the music library", library_stats.run),
]


def main():
    while True:
        print("\n" + "=" * 58)
        print("                    MUSIC LIBRARY TOOLS")
        print("=" * 58)

        for i, (description, _) in enumerate(TOOLS, 1):
            print(f"  {i}. {description}")

        print("\n  0. Exit")
        print("-" * 58)

        choice = input("Select a tool: ").strip()

        if choice == "0":
            print("\nExiting.\n")
            break

        try:
            option = int(choice)
            if option < 1 or option > len(TOOLS):
                raise ValueError
        except ValueError:
            print("\nInvalid choice. Please select a listed option.\n")
            continue

        description, tool = TOOLS[option - 1]
        print(f"\n{'=' * 58}\n  {description}\n{'=' * 58}\n")

        try:
            tool()
        except KeyboardInterrupt:
            print("\nOperation interrupted.\n")
        except Exception as e:
            print(f"\nTool failed: {e}\n")


if __name__ == "__main__":
    main()
