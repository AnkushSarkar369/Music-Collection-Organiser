"""Audit and optionally remove unused FLAC metadata padding.
Dry-run by default. Use --apply to remove padding.
Requires the system 'metaflac' command from the FLAC package.
"""

from pathlib import Path
import shutil
import subprocess
import sys

from config import ROOT

DESCRIPTION = "Audit and remove unused FLAC metadata padding"


def get_padding(file):
    result = subprocess.run(
        ["metaflac", "--list", "--block-type=PADDING", str(file)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    total = 0
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("length:"):
            total += int(line.split(":", 1)[1].strip())
    return total


def run():
    apply = "--apply" in sys.argv

    if shutil.which("metaflac") is None:
        raise RuntimeError(
            "metaflac was not found. Install the FLAC package "
            "(for Fedora: sudo dnf install flac)."
        )

    total_padding = 0
    files_with_padding = 0
    files_changed = 0
    errors = 0

    print("\n" + "=" * 72)
    print("  FLAC OPTIMIZATION")
    print("=" * 72)
    print(f"  Library: {ROOT}")
    print("  Operation: remove unused FLAC metadata padding")
    print("-" * 72)

    for file in sorted(ROOT.rglob("*.flac"), key=lambda p: str(p).casefold()):
        try:
            padding = get_padding(file)
            if padding == 0:
                continue

            files_with_padding += 1
            total_padding += padding
            print(f"  {padding:>10,} bytes  {file.relative_to(ROOT)}")

            if apply:
                result = subprocess.run(
                    [
                        "metaflac",
                        "--dont-use-padding",
                        "--remove",
                        "--block-type=PADDING",
                        str(file),
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr.strip())
                files_changed += 1

        except Exception as e:
            errors += 1
            print(f"  [!] {file.relative_to(ROOT)}: {e}")

    print("\n" + "=" * 72)
    print(f"  FLAC files with padding : {files_with_padding:,}")
    print(f"  Padding found           : {total_padding:,} bytes")
    print(f"                           {total_padding / 1024:.2f} KiB")
    print(f"                           {total_padding / (1024 ** 2):.2f} MiB")
    print(f"  Errors                  : {errors:,}")

    if apply:
        print(f"  Files modified          : {files_changed:,}")
        print("\n  DONE — padding removed.")
    else:
        print("\n  DRY RUN — nothing was modified.")
        print("  Run with --apply to remove the padding.")

    print("=" * 72 + "\n")


if __name__ == "__main__":
    run()
