"""Core TikZ extraction functionality.

This module provides functions for discovering files, extracting TikZ blocks,
and generating output files and AI context. It serves as the core engine for
the tikz-extractor package, handling file system operations, regex pattern
matching, and metadata generation.

The module is designed to be robust and handle various edge cases including
encoding issues, unreadable files, and malformed TikZ blocks.

Example:
    Basic usage for extracting TikZ blocks from a directory:
    
    >>> from pathlib import Path
    >>> from tikz_extractor.extractor import extract_from_directory
    >>> 
    >>> src_dir = Path("./documents")
    >>> out_dir = Path("./extracted")
    >>> extensions = [".tex", ".md"]
    >>> 
    >>> metadata = extract_from_directory(src_dir, out_dir, extensions)
    >>> print(f"Extracted {len(metadata)} TikZ blocks")
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


def find_files(src: Path, exts: List[str]) -> List[Path]:
    """Recursively discover files matching specified extensions.

    Scans the source directory recursively to find all files that match any of
    the specified extensions. Extensions are normalized to ensure consistent
    matching regardless of whether they include leading dots.

    Args:
        src (Path): Source directory to scan recursively. Must be a valid directory.
        exts (List[str]): List of file extensions to match. Extensions can be
            provided with or without leading dots (e.g., ['.tex', 'md']).

    Returns:
        List[Path]: List of Path objects for all files matching the specified
            extensions. Returns empty list if no matches found.

    Example:
        >>> from pathlib import Path
        >>> src = Path("./documents")
        >>> extensions = [".tex", ".md", "py"]
        >>> files = find_files(src, extensions)
        >>> print(f"Found {len(files)} files")

    Note:
        This function uses Path.rglob() for efficient recursive directory
        traversal and handles both Unix and Windows path separators.
    """
    # Normalize extensions to ensure they start with a dot
    normalized_exts = []
    for ext in exts:
        if not ext.startswith("."):
            normalized_exts.append("." + ext)
        else:
            normalized_exts.append(ext)

    found_files = []
    for ext in normalized_exts:
        # Use rglob for recursive search with pattern matching
        pattern = f"*{ext}"
        found_files.extend(src.rglob(pattern))

    return found_files


# Compiled regex pattern for TikZ block matching with multi-line support
# Pattern explanation:
# - (?s): DOTALL flag - makes '.' match newlines for multi-line blocks
# - \\begin\{tikzpicture\}: Literal match for LaTeX begin environment
# - .*?: Non-greedy match for any content (including newlines)
# - \\end\{tikzpicture\}: Literal match for LaTeX end environment
TIKZ_RE = re.compile(r"(?s)\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}")


def _format_tikz_content(content: str) -> str:
    """Format TikZ content with proper indentation and clean structure.

    Takes raw TikZ content and formats it with consistent indentation,
    removes excessive whitespace, and ensures clean line breaks.

    Args:
        content (str): Raw TikZ block content to format.

    Returns:
        str: Formatted TikZ content with proper indentation.
    """
    lines = content.split("\n")
    formatted_lines = []
    indent_level = 0

    for line in lines:
        # Remove leading/trailing whitespace
        clean_line = line.strip()

        # Skip empty lines
        if not clean_line:
            continue

        # Decrease indent for end statements
        if clean_line.startswith("\\end{"):
            indent_level = max(0, indent_level - 1)

        # Add proper indentation
        if clean_line.startswith("\\begin{tikzpicture}"):
            formatted_lines.append(clean_line)
            indent_level = 1
        elif clean_line.startswith("\\end{tikzpicture}"):
            formatted_lines.append(clean_line)
        else:
            # Indent content inside tikzpicture
            formatted_lines.append("  " + clean_line)

    # Join with newlines and ensure proper ending
    result = "\n".join(formatted_lines)
    if not result.endswith("\n"):
        result += "\n"

    return result


def sanitize_name(path: Path) -> str:
    """Convert file paths to safe filename components.

    Transforms a file path into a safe filename by using just the filename
    without the full path, making output filenames much shorter and cleaner.

    Args:
        path (Path): Path object to sanitize. Can be absolute or relative path.

    Returns:
        str: Sanitized filename string safe for cross-platform use.

    Example:
        >>> from pathlib import Path
        >>> path = Path("src/diagrams/network.tex")
        >>> safe_name = sanitize_name(path)
        >>> print(safe_name)  # Output: "network.tex"

    Note:
        This function now returns just the filename for cleaner output.
        If there are naming conflicts, the directory structure will be
        preserved in the AI context file headers.
    """
    # Just return the filename without the full path for cleaner names
    sanitized = path.name
    return sanitized


def extract_tikz_from_text(text: str) -> List[str]:
    """Extract TikZ blocks from text using regex pattern matching.

    Searches the provided text for complete TikZ picture environments using
    a compiled regex pattern. The pattern matches from \\begin{tikzpicture}
    to \\end{tikzpicture} including all content in between, handling multi-line
    blocks correctly.

    Args:
        text (str): Text content to search for TikZ blocks. Can contain multiple
            TikZ environments and other content.

    Returns:
        List[str]: List of complete TikZ block strings found in the text.
            Each string includes the full environment from begin to end.
            Returns empty list if no TikZ blocks are found.

    Example:
        >>> content = '''
        ... Some text here
        ... \\begin{tikzpicture}
        ... \\draw (0,0) -- (1,1);
        ... \\end{tikzpicture}
        ... More content
        ... '''
        >>> blocks = extract_tikz_from_text(content)
        >>> print(f"Found {len(blocks)} TikZ blocks")

    Note:
        The regex pattern uses non-greedy matching to correctly handle
        multiple TikZ blocks within the same text content.
    """
    return TIKZ_RE.findall(text)


def write_extracted_blocks(
    blocks: List[str], src_path: Path, out_dir: Path, start_counter: int = 1
) -> List[Dict[str, any]]:
    """Write extracted TikZ blocks to individual .tex files and generate metadata.

    Creates individual .tex files for each TikZ block with descriptive filenames
    based on the source path. Also generates structured metadata for each block
    that can be used for further processing or AI context generation.

    Args:
        blocks (List[str]): List of TikZ block strings to write. Each string
            should be a complete TikZ environment.
        src_path (Path): Source file path where blocks were extracted from.
            Used for generating descriptive output filenames.
        out_dir (Path): Output directory for .tex files. Directory will be
            created if it doesn't exist.

    Returns:
        List[Dict[str, any]]: List of metadata dictionaries for each written
            block. Each dictionary contains:
            - 'source': Original source file path as string
            - 'out_path': Generated output file path as string
            - 'index': Block number within the source file (1-based)
            - 'content': Complete TikZ block content as string

    Example:
        >>> from pathlib import Path
        >>> blocks = ['\\begin{tikzpicture}\\draw (0,0) -- (1,1);\\end{tikzpicture}']
        >>> src = Path("diagrams/flow.tex")
        >>> out = Path("./extracted")
        >>> metadata = write_extracted_blocks(blocks, src, out)
        >>> print(metadata[0]['out_path'])  # tikz_1.tex

    Note:
        Output filenames follow the pattern: tikz_{index}.tex for cleaner,
        shorter filenames. Source information is preserved in metadata.
    """
    # Create output directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata = []
    sanitized_source = sanitize_name(src_path)

    for index, block in enumerate(blocks):
        # Generate unique filename for each block - much shorter now
        global_index = start_counter + index
        filename = f"tikz_{global_index}.tex"
        out_path = out_dir / filename

        # Format the TikZ content with proper indentation
        formatted_block = _format_tikz_content(block)

        # Write formatted block to file
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(formatted_block)

        # Create metadata entry
        block_metadata = {
            "source": str(src_path),
            "out_path": str(out_path),
            "index": global_index,
            "content": formatted_block,
        }
        metadata.append(block_metadata)

    return metadata


def build_ai_context(metadata: List[Dict[str, any]], ai_file: Path) -> None:
    """Build AI context file with concatenated TikZ blocks and headers.

    Creates a consolidated text file containing all extracted TikZ blocks
    with structured headers indicating source files and snippet names. This
    format is optimized for consumption by AI models and LLMs.

    Args:
        metadata (List[Dict[str, any]]): List of metadata dictionaries from
            extracted blocks. Each dictionary should contain 'source',
            'out_path', and 'content' keys.
        ai_file (Path): Path where AI context file should be written. Parent
            directories will be created if they don't exist.

    Example:
        >>> from pathlib import Path
        >>> metadata = [
        ...     {
        ...         'source': 'diagrams/flow.tex',
        ...         'out_path': 'extracted/diagrams__flow.tex__tikz1.tex',
        ...         'content': '\\begin{tikzpicture}\\draw (0,0) -- (1,1);\\end{tikzpicture}'
        ...     }
        ... ]
        >>> build_ai_context(metadata, Path("ai_context.txt"))

    Note:
        The output format includes source headers, snippet filenames, and
        content blocks separated by '---' dividers for clear delineation.
        The file is written with UTF-8 encoding for broad compatibility.
    """
    with open(ai_file, "w", encoding="utf-8") as f:
        for i, block_meta in enumerate(metadata):
            # Write snippet filename only (removed source header)
            snippet_name = Path(block_meta["out_path"]).name
            f.write(f"### {snippet_name}\n")
            # Write the TikZ content
            f.write(block_meta["content"])
            f.write("\n")

            # Add separator between blocks (except for the last one)
            if i < len(metadata) - 1:
                f.write("\n---\n\n")


def extract_from_directory(
    src: Path, out_dir: Path, exts: List[str]
) -> List[Dict[str, any]]:
    """Orchestrate complete TikZ extraction workflow from directory.

    This is the main orchestration function that coordinates the entire
    extraction process: file discovery, content reading, TikZ extraction,
    file writing, and metadata collection. It handles errors gracefully
    and continues processing even when individual files fail.

    Args:
        src (Path): Source directory to scan for files recursively. Must be
            a valid directory path.
        out_dir (Path): Output directory for extracted .tex files. Will be
            created if it doesn't exist.
        exts (List[str]): List of file extensions to process. Extensions
            can be provided with or without leading dots.

    Returns:
        List[Dict[str, any]]: List of all metadata dictionaries from extracted
            blocks across all processed files. Each dictionary contains source
            path, output path, index, and content information.

    Raises:
        No exceptions are raised. File-level errors (encoding issues, permission
        problems, etc.) are caught and the problematic files are skipped.

    Example:
        >>> from pathlib import Path
        >>> src_dir = Path("./latex_project")
        >>> out_dir = Path("./extracted_tikz")
        >>> extensions = [".tex", ".md"]
        >>>
        >>> all_metadata = extract_from_directory(src_dir, out_dir, extensions)
        >>> print(f"Successfully extracted {len(all_metadata)} TikZ blocks")
        >>>
        >>> # Generate AI context file
        >>> if all_metadata:
        ...     build_ai_context(all_metadata, Path("tikz_context.txt"))

    Note:
        This function is designed to be robust and will continue processing
        even if individual files cannot be read due to encoding issues,
        permission problems, or other I/O errors. Such files are silently
        skipped to ensure the overall extraction process completes successfully.
    """
    all_metadata = []

    # Find all files matching the specified extensions
    files_to_process = find_files(src, exts)

    for file_path in files_to_process:
        try:
            # Read file content with UTF-8 encoding
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract TikZ blocks from the content
            tikz_blocks = extract_tikz_from_text(content)

            # If blocks found, write them and collect metadata
            if tikz_blocks:
                start_counter = len(all_metadata) + 1
                metadata = write_extracted_blocks(
                    tikz_blocks, file_path, out_dir, start_counter
                )
                all_metadata.extend(metadata)

        except (UnicodeDecodeError, IOError, OSError) as e:
            # Skip unreadable files and continue processing
            # In a real implementation, we might want to log this
            continue

    return all_metadata
