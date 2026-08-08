# flac-library-tools

Personal maintenance toolkit for a FLAC/OPUS music library. One menu
(`master.py`), a handful of independent tools, one shared config.

## Running it

```
cd ~/Music/Songs/flac-library-tools
python3 master.py
```

Pick a number. `0` exits.

## Project structure

```
flac-library-tools/
├── config.py              <- the ONE file with your library path
├── master.py              <- menu, auto-discovers tools/
├── requirements.txt
└── tools/
    ├── __init__.py                    <- leave empty, don't delete
    ├── standardize_artist_names.py    <- normalize separators + rename map + alphabetize
    ├── find_replace_artist.py         <- targeted bulk rename (e.g. initials -> full name)
    ├── artist_frequency_report.py     <- song count per artist (read-only)
    ├── album_art_report.py            <- embedded cover art sizes/resolutions (read-only)
    └── bracket_tag_report.py          <- scans filenames for [tags] (read-only)
```

Three tools are **read-only** (reports only, never touch your files):
`artist_frequency_report.py`, `album_art_report.py`, `bracket_tag_report.py`.

Two tools **write tags**: `standardize_artist_names.py`, `find_replace_artist.py`.
Both are interactive and ask per-change confirmation (or "accept all").
Neither renames files or folders — they only edit metadata inside the FLAC/OPUS.

## If you change your library's folder location

Edit **one line** in `config.py`:

```python
ROOT = Path("/home/ankush/Music/Songs")
```

Nothing else references a path. That's the entire point of `config.py` —
every tool imports `ROOT` from here instead of hardcoding its own.

## If you want to rename your actual music folders/files

None of these five tools touch filenames or folder structure — they only
edit tags (artist field) or read data. If you want a folder/file renamer
later, that's a new tool, not a change to existing ones. Say so and it gets
added as `tools/rename_something.py` — same pattern, doesn't disturb the rest.

## Adding a new tool later

1. Create `tools/your_tool_name.py`
2. Give it two things:
   ```python
   from config import ROOT

   DESCRIPTION = "One line describing what this does"

   def run():
       ...your logic here...

   if __name__ == "__main__":
       run()
   ```
3. That's it. `master.py` finds it automatically next run — no registration,
   no editing the menu file.

## Cross-platform status

**Currently Linux-only, on purpose.** `config.py` has a hardcoded Linux path.
That was a deliberate simplification (you're not maintaining this from
multiple machines), not a limitation of the tool logic itself.

If you ever DO need it to run on another OS (e.g. Windows via WSL, or a
second machine):

- The actual scanning logic (`pathlib.Path`, `rglob`) is already
  OS-agnostic — it works identically on Linux/Mac/Windows.
- The only non-portable part is the hardcoded path string in `config.py`.
- Fix: replace the hardcoded line with an environment variable read, e.g.
  ```python
  import os
  ROOT = Path(os.environ["FLAC_LIBRARY_ROOT"])
  ```
  Then set `FLAC_LIBRARY_ROOT` differently per machine. This was the
  original plan before you decided Linux-only was enough — it's a five
  minute change if your situation changes later, not a rewrite.

## Dependencies

```
pip install -r requirements.txt
```

Currently just `mutagen`. If you add `artist_network_graph.py` back later,
it also needs `pyvis`.

## Deleted/rejected tools (for reference, don't recreate)

- `move.py` — embedded external art into FLACs then moved files to a "done"
  folder. Destructive (file-moving), deleted deliberately.
- `alphabeticalartist.py` / `sort_collab_artists.py` — merged into
  `standardize_artist_names.py`, don't recreate as separate files.
- `artsize.py`, `artistlist.py`, `Artist_Name.py`, `Replace_Artist_Name.py`,
  `square.py`, `Graph.py` — original standalone versions, superseded by the
  `tools/` versions above. Safe to delete from wherever they still exist.
