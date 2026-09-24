"""Report the formats and basic technical characteristics in the music library.
Read-only — does not modify any files.
"""

from collections import Counter, defaultdict
from pathlib import Path

from mutagen import File as MutagenFile
from mutagen.flac import FLAC

from config import ROOT

DESCRIPTION = "Report library formats, codecs, sample rates, and bit depths"


def format_size(size):
    if size >= 1024 ** 3:
        return f"{size / (1024 ** 3):.2f} GB"
    if size >= 1024 ** 2:
        return f"{size / (1024 ** 2):.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size:,} B"


def run():
    extension_counts = Counter()
    extension_sizes = Counter()
    technical = defaultdict(Counter)
    errors = 0

    for file in sorted(ROOT.rglob("*"), key=lambda p: str(p).casefold()):
        if not file.is_file():
            continue

        try:
            audio = MutagenFile(file)
        except Exception:
            continue

        if audio is None:
            continue

        extension = file.suffix.lower() or "[no extension]"
        extension_counts[extension] += 1
        extension_sizes[extension] += file.stat().st_size

        if extension not in {".flac", ".opus"}:
            continue

        try:
            info = audio.info
            sample_rate = getattr(info, "sample_rate", None)
            channels = getattr(info, "channels", None)
            bits = getattr(info, "bits_per_sample", None)
            bitrate = getattr(info, "bitrate", None)

            technical[extension][
                f"{sample_rate or '?'} Hz / "
                f"{bits or '?'}-bit / "
                f"{channels or '?'} ch"
            ] += 1

            if extension == ".opus" and bitrate:
                technical[extension][f"bitrate:{bitrate // 1000} kbps"] += 1

        except Exception:
            errors += 1

    print("\n" + "=" * 72)
    print("  LIBRARY FORMAT REPORT")
    print("=" * 72)
    print(f"  Library: {ROOT}")
    print("=" * 72)

    print("\n  FILE FORMAT SUMMARY")
    print("  " + "-" * 68)
    print(f"  {'Format':<12} {'Files':>10} {'Total Size':>16}")
    print("  " + "-" * 68)

    for extension in sorted(extension_counts):
        print(
            f"  {extension:<12} "
            f"{extension_counts[extension]:>10,} "
            f"{format_size(extension_sizes[extension]):>16}"
        )

    print("\n  FLAC TECHNICAL BREAKDOWN")
    print("  " + "-" * 68)
    flac_technical = {
        key: value
        for key, value in technical[".flac"].items()
        if not key.startswith("bitrate:")
    }

    if not flac_technical:
        print("  None")
    else:
        for key, count in sorted(flac_technical.items()):
            print(f"  {key:<36} {count:>6,}")

    print("\n  OPUS TECHNICAL BREAKDOWN")
    print("  " + "-" * 68)
    opus_technical = technical[".opus"]

    if not opus_technical:
        print("  None")
    else:
        for key, count in sorted(opus_technical.items()):
            print(f"  {key:<36} {count:>6,}")

    print("\n" + "=" * 72)
    print(f"  Errors: {errors:,}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    run()
