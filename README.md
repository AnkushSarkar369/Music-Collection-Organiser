# Music Collection Organiser

A personal toolkit for maintaining, auditing, and understanding a FLAC/Opus music library.

The project is deliberately small: one shared configuration, one master menu, and a set of independent tools. Each tool answers a different question or performs one focused operation rather than producing the same information in several decorative forms.

## What it does

### Artist

| Tool | Purpose |
|---|---|
| **Artist · Find & Replace** | Replace one specific artist name across the library. |
| **Artist · Frequency** | Count how many songs each artist appears on. |
| **Artist · Normalize** | Convert messy artist metadata into the canonical `Artist A; Artist B; Artist C` format, apply the rename map, and alphabetize collaborators. |

### Artwork

| Tool | Purpose |
|---|---|
| **Artwork · Audit** | Find missing artwork and artwork below `1000 × 1000`. |
| **Artwork · Inspect** | Report embedded artwork sizes, resolutions, averages, and extremes. |

### Composers

| Tool | Purpose |
|---|---|
| **Composers · Browse works** | Browse the works grouped by the current `composer` metadata field. |

> In this library, the `composer` field is currently used to group anime/franchise works rather than to represent the musical composer.

### Files

| Tool | Purpose |
|---|---|
| **Files · Bracket Tags** | Find and count `[bracketed]` annotations in filenames. |

### Library

| Tool | Purpose |
|---|---|
| **Library · List** | List songs alphabetically within each directory. |
| **Library · Overview** | Show per-directory FLAC/Opus counts, storage, artwork size, artist counts, and an overall library snapshot. |

## The menu

Run everything through `master.py`:

```text
1. Artist · Find & Replace
2. Artist · Frequency
3. Artist · Normalize
4. Artwork · Audit
5. Artwork · Inspect
6. Composers · Browse works
7. Files · Bracket Tags
8. Library · List
9. Library · Overview
0. Exit
```

The menu uses an explicit lookup table, so each option is tied directly to its corresponding tool module. Changing the displayed description does not change what gets executed.

## Artist metadata philosophy

Artist metadata has one canonical form:

```text
Artist A; Artist B; Artist C
```

`Artist · Normalize` is the boundary between messy input and canonical data. It accepts the supported variations such as `&`, `/`, `feat.`, `ft.`, and `featuring`, applies the project's rename rules, alphabetizes the artists, and writes the final value using `;`.

Every other artist-aware tool assumes the library has already been normalized and therefore splits artist fields **only on `;`**.

This gives the project a simple data contract:

```text
messy metadata
      ↓
Artist · Normalize
      ↓
A; B; C
      ↓
all other tools
```

Selected normalization rules include:

```text
A. R. Rahman       → Allah Rakha Rahman
R. D. Burman       → Rahul Dev Burman
Hemant Kumar       → Hemanta Mukhopadhyay
Hemanta Mukherjee  → Hemanta Mukhopadhyay
A & B              → A; B
```

The rename map lives in `tools/artist_standardize.py` and is intentionally explicit rather than hidden behind a general-purpose fuzzy-matching system.

## Safety model

The tools fall into two simple categories.

**Read-only tools** inspect the library and report information:

- `artist_frequency_report.py`
- `bracket_tag_report.py`
- `composer_report.py`
- `cover_art_audit.py`
- `cover_art_report.py`
- `library_list.py`
- `library_stats.py`

**Metadata-writing tools** are:

- `artist_standardize.py`
- `artist_find_replace.py`

Neither metadata-writing tool renames files or folders. They only modify the embedded artist metadata of FLAC/Opus files.

`Artist · Normalize` is interactive: each proposed change can be applied, skipped, accepted for all remaining files, or cancelled.

## Installation

Clone the repository and install the single dependency:

```bash
pip install -r requirements.txt
```

The project currently depends on [Mutagen](https://mutagen.readthedocs.io/) for FLAC and Ogg Opus metadata handling.

## Configuration

The library root is defined once in `config.py`:

```python
ROOT = Path("/home/ankush/Music/Songs")
```

Change that one value if the library lives somewhere else. Every tool imports `ROOT` from the shared configuration instead of maintaining its own path.

The current configuration is intentionally Linux-specific. The scanning code itself uses `pathlib` and recursive filesystem traversal, so portability is mostly a configuration concern rather than a rewrite of the tools.

## Project structure

```text
Music-Collection-Organiser/
├── config.py
├── master.py
├── requirements.txt
└── tools/
    ├── __init__.py
    ├── artist_find_replace.py
    ├── artist_frequency_report.py
    ├── artist_standardize.py
    ├── bracket_tag_report.py
    ├── composer_report.py
    ├── cover_art_audit.py
    ├── cover_art_report.py
    ├── library_list.py
    └── library_stats.py
```

`tools/__init__.py` is intentionally empty; it simply makes `tools` a Python package for the imports used by `master.py`.

## Design principles

### One tool, one job

A report should answer a distinct question. `Library · List` tells you where songs are; `Library · Overview` tells you how the library is distributed. `Artwork · Audit` finds problems; `Artwork · Inspect` describes the artwork collection.

### Canonical data first

Normalization happens once. Everything downstream can then operate on a predictable representation instead of repeatedly trying to interpret every possible form of messy metadata.

### Explicit beats clever

The project favours straightforward lookup tables, explicit rename maps, simple filesystem traversal, and small independent scripts. There is no plugin framework, dynamic discovery system, or unnecessary abstraction layer.

### Reports do not modify the library

Unless a tool is explicitly a metadata-writing tool, running it should only inspect and report.

## Running it

From the project root:

```bash
python3 master.py
```

Then select a tool by number. `0` exits.

Individual tools can also be run directly, for example:

```bash
python3 tools/library_stats.py
python3 tools/artist_frequency_report.py
```

## Adding a tool

A new tool should remain small and focused:

```python
from config import ROOT

DESCRIPTION = "One-line description"


def run():
    ...


if __name__ == "__main__":
    run()
```

Then add the module and its explicit `(description, module.run)` entry to `TOOLS` in `master.py`.

No framework is needed. If a new feature can be expressed as one focused tool, it should be.

## Scope

This is a personal maintenance project. It is built around the structure and metadata conventions of one music library, rather than trying to become a universal music-management application.

That constraint is intentional. The goal is a small collection of dependable tools, not a second music player disguised as a Python project.
