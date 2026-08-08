"""
Shared config for flac-library-tools.
Every tool imports ROOT from here instead of hardcoding its own path.
"""

from pathlib import Path

ROOT = Path("/home/ankush/Music/Songs")

if not ROOT.exists():
    raise RuntimeError(f"Library root doesn't exist: {ROOT}")