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
    cover_art_audit,
    cover_art_report,
    cover_art_replace,
    cover_art_replace_embed,
    flac_optimize,
    library_format_report,
    library_list,
    library_stats,
    tag_audit,
)


TOOLS = [
    ("Artist · Find & Replace - Replace specific artist names.", artist_find_replace.run),
    ("Artist · Frequency - Lists artists by track frequency.", artist_frequency_report.run),
    ("Artist · Normalize - Standardizes artist names, separators, and ordering.", artist_standardize.run),
    ("Artwork · Audit - Finds missing and low-resolution artwork.", cover_art_audit.run),
    ("Artwork · Inspect - Reports embedded artwork sizes and resolutions.", cover_art_report.run),
    ("Artwork · Replace Low-Res - Replaces low-resolution FLAC covers from Album Art.", cover_art_replace.menu),
    ("Artwork · Replace / Embed - Replaces or embeds covers in FLAC and Opus files.", cover_art_replace_embed.menu),
    ("Composers · Browse works - Lists songs grouped by composer metadata.", composer_report.run),
    ("Files · Bracket Tags - Finds bracketed annotations in filenames.", bracket_tag_report.run),
    ("FLAC · Optimize - Audits and removes unused FLAC metadata padding.", flac_optimize.run),
    ("Library · Formats - Reports formats and technical audio characteristics.", library_format_report.run),
    ("Library · List - Lists songs alphabetically within directories.", library_list.run),
    ("Library · Overview - Shows per-directory counts, sizes, artwork, and artists.", library_stats.run),
    ("Metadata · Audit - Finds missing, extra, comma, and unsorted tags.", tag_audit.run),
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
