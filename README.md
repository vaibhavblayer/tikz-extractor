# TikZ Extractor CLI

A Python package for extracting TikZ picture environments from codebases and generating AI context files. This tool recursively scans directories, extracts TikZ blocks from various file types, saves them as individual `.tex` files, and creates a consolidated context file for AI model consumption.

## Features

- 🔍 **Recursive Directory Scanning**: Automatically finds TikZ blocks in specified file types
- 📄 **Multiple File Format Support**: Works with `.tex`, `.md`, `.py`, and other text files
- 🎯 **Smart Extraction**: Uses robust regex patterns to extract complete TikZ picture environments
- 📁 **Organized Output**: Saves each TikZ block as a separate `.tex` file with descriptive names
- 🤖 **AI Context Generation**: Creates a consolidated file with all extracted blocks for LLM consumption
- 🖥️ **CLI Interface**: Easy-to-use command-line interface with flexible options
- 📦 **Python Module**: Importable package for programmatic usage
- 🔧 **Dry Run Mode**: Preview extraction results without writing files
- 📝 **Verbose Logging**: Detailed processing information when needed

## Installation

### Using pip

```bash
pip install tikz-extractor
```

### Using Poetry

```bash
poetry add tikz-extractor
```

### Development Installation

```bash
git clone https://github.com/vaibhavblayer/tikz-extractor.git
cd tikz-extractor
poetry install --with dev
```

## Usage

### Command Line Interface

#### Basic Usage

Extract TikZ blocks from the current directory:

```bash
tikz-extract
```

#### Advanced Usage

```bash
# Specify source and output directories
tikz-extract --src ./documents --out ./extracted_tikz

# Process specific file types
tikz-extract --ext .tex,.md,.rst

# Generate custom AI context file
tikz-extract --ai-file my_tikz_context.txt

# Dry run to preview results
tikz-extract --dry-run --verbose

# Full example with all options
tikz-extract \
  --src ./latex_project \
  --out ./tikz_output \
  --ext .tex,.md \
  --ai-file tikz_for_ai.txt \
  --verbose
```

#### CLI Parameters

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--src` | `-s` | `.` | Source directory to scan recursively |
| `--out` | `-o` | `tikz` | Output directory for extracted `.tex` files |
| `--ext` | `-e` | `.tex,.md,.py` | Comma-separated list of file extensions to process |
| `--ai-file` | `-a` | `ai_context.txt` | Path for the AI context file |
| `--dry-run` | `-d` | `False` | Preview mode - show results without writing files |
| `--verbose` | `-v` | `False` | Enable detailed logging output |
| `--help` | `-h` | - | Show help message and exit |

### Python Module Interface

#### Basic Programmatic Usage

```python
from tikz_extractor import extractor
from pathlib import Path

# Extract TikZ blocks from a directory
src_dir = Path("./documents")
out_dir = Path("./extracted")
extensions = [".tex", ".md"]

metadata = extractor.extract_from_directory(src_dir, out_dir, extensions)

# Process the results
for block_info in metadata:
    print(f"Extracted from: {block_info['source']}")
    print(f"Saved to: {block_info['out_path']}")
    print(f"Block index: {block_info['index']}")
```

#### Advanced Programmatic Usage

```python
from tikz_extractor.extractor import (
    find_files,
    extract_tikz_from_text,
    write_extracted_blocks,
    build_ai_context
)
from pathlib import Path

# Step-by-step extraction process
src_dir = Path("./my_project")
out_dir = Path("./tikz_blocks")
extensions = [".tex", ".md"]

# 1. Find all relevant files
files = find_files(src_dir, extensions)
print(f"Found {len(files)} files to process")

# 2. Process each file
all_metadata = []
for file_path in files:
    try:
        content = file_path.read_text(encoding='utf-8')
        tikz_blocks = extract_tikz_from_text(content)
        
        if tikz_blocks:
            metadata = write_extracted_blocks(tikz_blocks, file_path, out_dir)
            all_metadata.extend(metadata)
            print(f"Extracted {len(tikz_blocks)} blocks from {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# 3. Generate AI context file
if all_metadata:
    ai_file = Path("tikz_context.txt")
    build_ai_context(all_metadata, ai_file)
    print(f"AI context file created: {ai_file}")
```

#### Individual Function Usage

```python
from tikz_extractor.extractor import extract_tikz_from_text, sanitize_name
from pathlib import Path

# Extract TikZ blocks from text content
latex_content = """
Some text here...
\\begin{tikzpicture}
\\draw (0,0) -- (1,1);
\\end{tikzpicture}
More content...
"""

blocks = extract_tikz_from_text(latex_content)
print(f"Found {len(blocks)} TikZ blocks")

# Generate safe filenames
path = Path("src/diagrams/flow_chart.tex")
safe_name = sanitize_name(path)
print(f"Safe filename: {safe_name}")  # Output: src__diagrams__flow_chart.tex
```

## Output Format

### Extracted Files

Each TikZ block is saved as a separate `.tex` file with the naming pattern:
```
{sanitized_source_path}__tikz{index}.tex
```

**Examples:**
- `src/diagrams/network.tex` → `src__diagrams__network.tex__tikz1.tex`
- `docs/README.md` → `docs__README.md__tikz1.tex`

### AI Context File

The AI context file contains all extracted TikZ blocks with structured headers:

```
### Source: src/diagrams/network.tex
### Snippet: src__diagrams__network.tex__tikz1.tex
\begin{tikzpicture}
\node (A) at (0,0) {Start};
\node (B) at (2,0) {End};
\draw[->] (A) -- (B);
\end{tikzpicture}

---

### Source: docs/README.md
### Snippet: docs__README.md__tikz1.tex
\begin{tikzpicture}
\draw (0,0) circle (1);
\end{tikzpicture}

---
```

## Examples

### Example 1: LaTeX Project

```bash
# Extract from a LaTeX thesis project
tikz-extract \
  --src ./thesis \
  --out ./thesis_tikz \
  --ext .tex \
  --ai-file thesis_diagrams.txt \
  --verbose
```

### Example 2: Documentation with Embedded TikZ

```bash
# Process Markdown documentation with TikZ diagrams
tikz-extract \
  --src ./docs \
  --ext .md,.rst \
  --out ./doc_diagrams \
  --ai-file documentation_tikz.txt
```

### Example 3: Mixed Codebase

```bash
# Extract from various file types in a research project
tikz-extract \
  --src ./research_project \
  --ext .tex,.md,.py,.txt \
  --out ./all_tikz \
  --dry-run  # Preview first
```

## API Reference

### Core Functions

#### `extract_from_directory(src: Path, out_dir: Path, exts: List[str]) -> List[Dict]`

Orchestrates the complete TikZ extraction workflow.

**Parameters:**
- `src`: Source directory to scan
- `out_dir`: Output directory for extracted files
- `exts`: List of file extensions to process

**Returns:** List of metadata dictionaries for each extracted block

#### `find_files(src: Path, exts: List[str]) -> List[Path]`

Recursively finds files with specified extensions.

**Parameters:**
- `src`: Directory to search
- `exts`: List of file extensions (with or without leading dots)

**Returns:** List of Path objects for matching files

#### `extract_tikz_from_text(text: str) -> List[str]`

Extracts TikZ picture environments from text content.

**Parameters:**
- `text`: Text content to search

**Returns:** List of complete TikZ block strings

#### `write_extracted_blocks(blocks: List[str], src_path: Path, out_dir: Path) -> List[Dict]`

Writes TikZ blocks to individual files and generates metadata.

**Parameters:**
- `blocks`: List of TikZ block strings
- `src_path`: Original source file path
- `out_dir`: Output directory

**Returns:** List of metadata dictionaries

#### `build_ai_context(metadata: List[Dict], ai_file: Path) -> None`

Creates an AI context file with all extracted blocks.

**Parameters:**
- `metadata`: List of block metadata
- `ai_file`: Path for the output context file

## Error Handling

The tool is designed to be robust and continue processing even when encountering issues:

- **Unreadable files**: Skipped with optional logging
- **Encoding issues**: Attempts UTF-8, skips on failure
- **Permission errors**: Skipped with warning messages
- **Missing directories**: Output directories are created automatically
- **Malformed TikZ blocks**: Extracts what's parseable
- **Empty results**: Informative message, graceful exit

## Development

### Setting up Development Environment

```bash
git clone https://github.com/vaibhavblayer/tikz-extractor.git
cd tikz-extractor
poetry install --with dev
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=tikz_extractor

# Run specific test file
poetry run pytest tests/test_extractor.py -v
```

### Code Quality

```bash
# Format code
poetry run black tikz_extractor tests

# Sort imports
poetry run isort tikz_extractor tests

# Lint code
poetry run flake8 tikz_extractor tests

# Type checking
poetry run mypy tikz_extractor
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- **Issues**: [GitHub Issues](https://github.com/vaibhavblayer/tikz-extractor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vaibhavblayer/tikz-extractor/discussions)

## Related Projects

- [TikZ](https://tikz.dev/) - The original TikZ package for LaTeX
- [LaTeX](https://www.latex-project.org/) - Document preparation system
- [Click](https://click.palletsprojects.com/) - Python CLI framework used by this project