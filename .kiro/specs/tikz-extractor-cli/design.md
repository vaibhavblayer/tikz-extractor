# Design Document

## Overview

The TikZ Extractor CLI is designed as a lightweight Python package that provides both command-line and programmatic interfaces for extracting TikZ picture environments from codebases. The system follows a modular architecture with clear separation between core extraction logic, CLI interface, and file I/O operations.

The package uses Poetry for dependency management and packaging, Click for CLI functionality, and standard Python libraries for file operations and regex pattern matching. The design emphasizes minimal dependencies, robust error handling, and extensibility for future enhancements.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Module    │    │  Core Extractor │    │  File I/O Utils │
│   (cli.py)      │───▶│   (extractor.py)│───▶│   (built-in)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Click Args    │    │   TikZ Regex    │    │   Path Objects  │
│   Validation    │    │   Processing    │    │   File Writing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Module Structure

```
tikz_extractor/
├── __init__.py          # Package initialization and exports
├── extractor.py         # Core extraction logic and utilities
├── cli.py              # Click-based command-line interface
└── exceptions.py       # Custom exception classes (future)
```

### Data Flow

1. **Input Processing**: CLI arguments or function parameters specify source directory, output directory, file extensions, and options
2. **File Discovery**: Recursive directory traversal identifies files matching specified extensions
3. **Content Extraction**: Regex pattern matching extracts TikZ blocks from file contents
4. **File Generation**: Individual .tex files are created for each extracted block with sanitized names
5. **Metadata Collection**: Structured metadata is collected for each extraction operation
6. **AI Context Generation**: All extracted blocks are concatenated into a single context file with headers

## Components and Interfaces

### Core Extractor Module (extractor.py)

#### Primary Functions

**`find_files(src: Path, exts: List[str]) -> List[Path]`**
- Recursively discovers files matching specified extensions
- Normalizes extension formats (handles with/without leading dots)
- Returns list of Path objects for processing

**`extract_tikz_from_text(text: str) -> List[str]`**
- Uses compiled regex pattern to find TikZ blocks
- Handles multi-line tikzpicture environments
- Returns list of complete TikZ block strings

**`sanitize_name(path: Path) -> str`**
- Converts file paths to safe filename components
- Replaces path separators with double underscores
- Ensures cross-platform compatibility

**`write_extracted_blocks(blocks: List[str], src_path: Path, out_dir: Path) -> List[Dict]`**
- Creates output directory if needed
- Writes each block to individual .tex file
- Generates structured metadata for each block
- Returns metadata list for further processing

**`build_ai_context(metadata: List[Dict], ai_file: Path) -> None`**
- Formats extracted blocks with source headers
- Creates concatenated context file for AI consumption
- Uses consistent formatting with separators

**`extract_from_directory(src: Path, out_dir: Path, exts: List[str]) -> List[Dict]`**
- Orchestrates complete extraction workflow
- Handles file reading errors gracefully
- Returns comprehensive metadata for all extractions

#### Regex Pattern Design

```python
TIKZ_RE = re.compile(r"(?s)\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}")
```

- Uses `(?s)` flag for DOTALL mode to handle multi-line blocks
- Non-greedy matching (`.*?`) to handle multiple blocks in single file
- Literal matching of LaTeX environment delimiters

### CLI Module (cli.py)

#### Command Interface

**Main Command: `tikz-extract`**
- Uses Click framework for argument parsing and validation
- Provides both short and long flag options
- Includes comprehensive help text with examples

#### Parameter Design

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| --src | -s | . | Source directory to scan |
| --out | -o | tikz | Output directory for .tex files |
| --ext | -e | .tex,.md,.py | Comma-separated file extensions |
| --ai-file | -a | ai_context.txt | AI context file path |
| --dry-run | -d | False | Preview mode without file writing |
| --verbose | -v | False | Detailed output logging |

#### Error Handling Strategy

- Graceful handling of invalid paths
- Clear error messages for user guidance
- Continuation on individual file failures
- Informative output for empty results

### Package Interface (__init__.py)

```python
"""tikz_extractor package"""
__version__ = "0.1.0"
__all__ = ["extractor", "cli"]

from . import extractor, cli
```

- Exposes core modules for programmatic use
- Maintains version information
- Provides clean import interface

## Data Models

### Extraction Metadata Structure

```python
{
    'source': str,      # Original file path
    'out_path': str,    # Generated .tex file path
    'index': int,       # Block number within source file
    'content': str,     # Complete TikZ block content
}
```

### AI Context File Format

```
### Source: path/to/source.ext
### Snippet: filename__tikz1.tex
\begin{tikzpicture}
[TikZ content]
\end{tikzpicture}

---

### Source: path/to/source.ext
### Snippet: filename__tikz2.tex
[Next TikZ block]

---
```

### File Naming Convention

**Pattern**: `{sanitized_source_path}__tikz{index}.tex`

**Examples**:
- `src/diagrams/flow.tex` → `src__diagrams__flow.tex__tikz1.tex`
- `docs/README.md` → `docs__README.md__tikz1.tex`

## Error Handling

### Exception Categories

1. **File System Errors**
   - Unreadable files: Skip with optional logging
   - Permission errors: Skip with warning message
   - Missing directories: Auto-create output directories

2. **Content Processing Errors**
   - Encoding issues: Attempt UTF-8, skip on failure
   - Malformed TikZ blocks: Extract what's parseable
   - Empty files: Skip silently

3. **CLI Argument Errors**
   - Invalid paths: Clear error message and exit
   - Invalid extensions: Warning with fallback to defaults
   - Conflicting options: Validation with helpful suggestions

### Recovery Strategies

- **Continue on Error**: Individual file failures don't stop processing
- **Informative Logging**: Clear messages about skipped files when verbose
- **Graceful Degradation**: Partial results better than complete failure
- **User Feedback**: Progress indication for large directory trees

## Testing Strategy

### Unit Testing Approach

**Test Structure**:
```
tests/
├── __init__.py
├── test_extractor.py       # Core extraction function tests
├── test_cli.py            # CLI interface tests
├── fixtures/              # Sample files for testing
│   ├── sample.tex         # File with TikZ blocks
│   ├── sample.md          # Markdown with TikZ
│   └── empty.py           # File without TikZ
└── conftest.py           # Pytest configuration and fixtures
```

### Test Categories

1. **Function-Level Unit Tests**
   - `test_find_files()`: Directory traversal and filtering
   - `test_extract_tikz_from_text()`: Regex pattern matching
   - `test_sanitize_name()`: Path sanitization logic
   - `test_write_extracted_blocks()`: File I/O operations
   - `test_build_ai_context()`: Context file generation

2. **Integration Tests**
   - End-to-end extraction workflow
   - CLI command execution with various parameters
   - File system integration with temporary directories
   - Error handling scenarios

3. **Edge Case Testing**
   - Empty directories and files
   - Files with multiple TikZ blocks
   - Nested TikZ environments
   - Unicode and special characters in paths
   - Large files and directories

### Test Fixtures

**Sample TikZ Content**:
```latex
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
```

**Test Directory Structure**:
```
fixtures/
├── nested/
│   └── deep.tex           # Nested directory test
├── multi_tikz.tex         # Multiple blocks in one file
├── no_tikz.py            # File without TikZ blocks
└── mixed_content.md      # Markdown with embedded TikZ
```

### Continuous Integration

**GitHub Actions Workflow**:
- Python 3.10+ compatibility testing
- Cross-platform testing (Linux, macOS, Windows)
- Code quality checks (flake8, black, mypy)
- Test coverage reporting
- Automated PyPI publishing on releases

## Performance Considerations

### Scalability Factors

1. **File System Performance**
   - Efficient directory traversal using `Path.rglob()`
   - Lazy evaluation for large directory trees
   - Memory-conscious file reading (one file at a time)

2. **Regex Performance**
   - Compiled regex pattern for reuse
   - Non-greedy matching to minimize backtracking
   - Single-pass extraction per file

3. **Memory Management**
   - Process files individually to limit memory usage
   - Stream-based approach for large files (future enhancement)
   - Garbage collection friendly metadata structures

### Optimization Opportunities

- **Parallel Processing**: Multi-threading for independent file processing
- **Caching**: Compiled regex patterns and path operations
- **Streaming**: Large file handling without full memory load
- **Filtering**: Early exclusion of binary files and large non-text files

## Security Considerations

### Input Validation

- Path traversal prevention in file operations
- Extension validation to prevent arbitrary file processing
- Size limits for individual files (future enhancement)

### File System Safety

- Safe filename generation with character sanitization
- Output directory creation with appropriate permissions
- Atomic file writing to prevent corruption

### Content Safety

- No code execution from extracted content
- Safe regex patterns without catastrophic backtracking
- UTF-8 encoding enforcement for text processing

## Future Enhancements

### Extensibility Points

1. **Custom TikZ Patterns**: Configurable regex patterns for different TikZ variants
2. **Output Formats**: JSON, YAML, or XML metadata output options
3. **Filtering Options**: Content-based filtering and block validation
4. **Integration APIs**: REST API or plugin architecture for external tools
5. **Performance Optimizations**: Parallel processing and streaming for large codebases

### Plugin Architecture (Future)

```python
class TikZExtractorPlugin:
    def pre_process(self, content: str) -> str: ...
    def post_process(self, blocks: List[str]) -> List[str]: ...
    def custom_naming(self, path: Path, index: int) -> str: ...
```

This design provides a solid foundation for the TikZ Extractor CLI while maintaining simplicity, reliability, and extensibility for future enhancements.