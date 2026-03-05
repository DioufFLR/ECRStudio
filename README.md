# ECRStudio

Editeur graphique pour fichiers **ECR** (Ecriture Comptable Recapitulative) utilises par **ISACOMPTA Connect** (ISAgri / Bobbee).

Les fichiers ECR sont des fichiers texte a format positionnel strict (largeur fixe) permettant d'importer des donnees comptables dans ISACOMPTA.

## Features

- **Open / Edit / Save** ECR files with full field-level editing
- **Flat list & hierarchical tree view** (VER > DOS > EXO > ECR > MVT...)
- **Validation engine** — checks hierarchy, required fields, dates, debit/credit balance
- **Add / Duplicate / Delete / Move lines** with hierarchy-aware placement
- **New file wizard** — create an ECR file from scratch step by step
- **Undo / Redo** (Ctrl+Z / Ctrl+Y, 50 levels)
- **Search & Replace** across all lines
- **Export to CSV** for review in Excel
- **Side-by-side file comparison** with field-level diff
- **Dark / Light theme** toggle with saved preference
- **Required field indicators** (OBL column) with visual highlighting
- **Right-click context menu** for quick actions
- **Full keyboard shortcuts** (see below)

## Supported ECR record types

| Type | Description | Fields |
|------|-------------|--------|
| VER | File header | 6 |
| DOS | Accounting folder | 15 |
| EXO | Fiscal year | 7 |
| CPT | Chart of accounts | 54 |
| ECR | Journal entry | 37 |
| MVT | Movement (entry detail) | 40 |
| TVA | VAT code | 20 |
| JOU | Journal | 15 |
| ECHMVT | Payment schedule | 13 |
| ANAMVT | Analytical movement | 6 |
| TIERS | Third party | 65 |

## Installation

### Prerequisites

- Python 3.10+ with tkinter (included by default)

```bash
# macOS
brew install python@3.12
# or if already installed:
python3 --version

# Windows
# Download from https://www.python.org/downloads/
```

### Run

```bash
git clone https://github.com/geoffreyfleur/ECRStudio.git
cd ECRStudio
python3 main.py
```

### Build standalone .exe (Windows)

```bash
pip install pyinstaller
python scripts/build_exe.py
# Output: dist/ECRStudio.exe
```

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file (wizard) |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+D` | Duplicate line |
| `Ctrl+H` | Search & Replace |
| `Ctrl+Up/Down` | Move line up/down |
| `Insert` | Add new line |
| `Delete` | Delete line |
| `F5` | Validate file |
| `Ctrl+Q` | Quit |

## ECR file format

See [docs/FORMAT_ECR.md](docs/FORMAT_ECR.md) for the complete ECR format reference.

Key rules:
- Encoding: ANSI (latin-1)
- Line endings: `\r\n` (Windows)
- Alpha fields: left-aligned, space-padded
- Num fields: right-aligned, zero-padded
- Date fields: `jjmmaaaa` format

## Project structure

```
ECRStudio/
├── main.py                 # Entry point
├── ecrstudio/
│   ├── app.py              # Main application window
│   ├── structures.py       # ECR field definitions
│   ├── parser.py           # File I/O and field manipulation
│   ├── constants.py        # Colors, hierarchy, themes
│   ├── themes.py           # Dark/light theme manager
│   ├── validator.py        # File validation engine
│   ├── tree_builder.py     # Hierarchical tree builder
│   ├── dialogs.py          # Add line, search/replace dialogs
│   ├── wizard.py           # New file creation wizard
│   ├── export.py           # CSV export
│   ├── diff.py             # File comparison
│   └── undo.py             # Undo/redo manager
├── examples/
│   └── exemple.ECR         # Sample ECR file
├── docs/
│   └── FORMAT_ECR.md       # ECR format documentation
└── scripts/
    └── build_exe.py        # PyInstaller build script
```

## License

MIT - See [LICENSE](LICENSE)

## Author

Geoffrey FLEUR — QA Tester @ Bobbee / ISAgri
