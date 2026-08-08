"""
Master menu for flac-library-tools.
Run this from the project root: python3 master.py
"""

from tools import (
    artist_find_replace,
    artist_frequency_report,
    artist_standardize,
    bracket_tag_report,
    composer_report,
    cover_art_missing,
    cover_art_report,
    cover_art_resolution_report,
    library_list,
    library_stats,
)


TOOLS = [
    ("Artist · Find & Replace", artist_find_replace.run),
    ("Artist · Frequency", artist_frequency_report.run),
    ("Artist · Normalize", artist_standardize.run),
    ("Artwork · Inspect", cover_art_report.run),
    ("Artwork · Missing", cover_art_missing.run),
    ("Artwork · Resolution", cover_art_resolution_report.run),
    ("Composers · Browse works", composer_report.run),
    ("Files · Bracket Tags", bracket_tag_report.run),
    ("Library · List", library_list.run),
    ("Library · Overview", library_stats.run),
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
