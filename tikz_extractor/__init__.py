"""TikZ Extractor Package

A Python package for extracting TikZ picture environments from codebases and
generating AI context files. This package provides both a command-line interface
and a programmatic API for integrating TikZ extraction into other applications.

The package is designed to be robust, handling various file types, encoding
issues, and edge cases while providing comprehensive user feedback and error
recovery.

Modules:
    extractor: Core extraction functionality with file discovery, regex processing,
        and metadata generation capabilities.
    cli: Click-based command-line interface with flexible options and user-friendly
        output formatting.

Example:
    Command-line usage:
    
    $ tikz-extract --src ./documents --out ./extracted --verbose
    
    Programmatic usage:
    
    >>> from tikz_extractor import extractor
    >>> from pathlib import Path
    >>> 
    >>> metadata = extractor.extract_from_directory(
    ...     Path("./docs"), Path("./extracted"), [".tex", ".md"]
    ... )
    >>> print(f"Extracted {len(metadata)} TikZ blocks")

Attributes:
    __version__ (str): Package version following semantic versioning.
    __all__ (List[str]): List of public modules available for import.

Note:
    This package requires Python 3.10+ and has minimal external dependencies,
    using only the Click library for CLI functionality.
"""

__version__ = "0.1.0"
__author__ = "vaibhavblayer"
__email__ = "vaibhavblayer@gmail.com"
__license__ = "MIT"
__all__ = ["extractor", "cli"]

# Import modules for programmatic access
from . import cli, extractor

# Convenience imports for common use cases
from .extractor import (
    build_ai_context,
    extract_from_directory,
    extract_tikz_from_text,
    find_files,
    sanitize_name,
    write_extracted_blocks,
)
