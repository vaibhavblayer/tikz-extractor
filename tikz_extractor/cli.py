"""Command-line interface for TikZ extractor.

This module provides a Click-based CLI for extracting TikZ picture environments
from codebases with flexible options and user-friendly output. It serves as the
primary interface for end users and provides comprehensive error handling,
validation, and user feedback.

The CLI supports dry-run mode for previewing results, verbose output for
detailed processing information, and flexible configuration of source
directories, output locations, and file types to process.

Example:
    Basic CLI usage:
    
    $ tikz-extract --src ./documents --out ./extracted --verbose
    $ tikz-extract --ext .tex,.md --dry-run
    $ tikz-extract --ai-file custom_context.txt
"""

import click
from pathlib import Path
from typing import List, Tuple, Dict

from . import extractor


@click.command()
@click.option(
    "--src",
    "-s",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path("."),
    help="Source directory to scan for TikZ blocks (default: current directory)",
)
@click.option(
    "--out",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("tikz"),
    help="Output directory for extracted .tex files (default: tikz)",
)
@click.option(
    "--ext",
    "-e",
    default=".tex,.md,.py",
    help="Comma-separated list of file extensions to scan (default: .tex,.md,.py)",
)
@click.option(
    "--ai-file",
    "-a",
    type=click.Path(path_type=Path),
    default=Path("ai_context.txt"),
    help="Path for AI context file containing all extracted blocks (default: ai_context.txt)",
)
@click.option(
    "--dry-run",
    "-d",
    is_flag=True,
    help="Preview extraction results without writing files",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Display detailed processing information"
)
def cli(
    src: Path, out: Path, ext: str, ai_file: Path, dry_run: bool, verbose: bool
) -> None:
    """Extract TikZ picture environments from codebases.

    This tool recursively scans the source directory for files with specified
    extensions, extracts TikZ blocks, and saves them as individual .tex files.
    It also generates an AI context file containing all extracted blocks.

    The extraction process is robust and handles various edge cases including
    encoding issues, unreadable files, and malformed content. Files that cannot
    be processed are skipped with appropriate user feedback.

    Args:
        src (Path): Source directory to scan recursively for TikZ blocks.
        out (Path): Output directory where extracted .tex files will be saved.
        ext (str): Comma-separated list of file extensions to process.
        ai_file (Path): Path for the AI context file containing all blocks.
        dry_run (bool): If True, preview results without writing files.
        verbose (bool): If True, display detailed processing information.

    Examples:
        Basic usage:

        $ tikz-extract

        Extract from specific directories:

        $ tikz-extract --src ./docs --out ./extracted_tikz

        Process only specific file types:

        $ tikz-extract --ext .tex,.md --verbose

        Preview without writing files:

        $ tikz-extract --dry-run --verbose

        Custom AI context file:

        $ tikz-extract --ai-file my_tikz_context.txt

    Note:
        The tool creates output directories automatically if they don't exist.
        In dry-run mode, no files are written but all processing steps are
        simulated to show what would happen.
    """
    # Validate and resolve paths
    src_path = _validate_source_path(src)
    out_path = _validate_output_path(out)
    ai_file_path = _validate_ai_file_path(ai_file)

    # Parse and validate extensions
    extensions = _parse_extensions(ext)

    if verbose:
        click.echo(f"Source directory: {src_path}")
        click.echo(f"Output directory: {out_path}")
        click.echo(f"AI context file: {ai_file_path}")
        click.echo(f"File extensions: {', '.join(extensions)}")
        click.echo(f"Dry run mode: {dry_run}")
        click.echo()

    # Perform extraction with dry-run and verbose support
    _perform_extraction(src_path, out_path, ai_file_path, extensions, dry_run, verbose)


def _perform_extraction(
    src_path: Path,
    out_path: Path,
    ai_file_path: Path,
    extensions: List[str],
    dry_run: bool,
    verbose: bool,
) -> None:
    """Perform TikZ extraction with dry-run and verbose support.

    This is the core extraction orchestration function that handles the complete
    workflow: file discovery, content processing, error handling, and user
    feedback. It provides comprehensive error recovery and detailed reporting.

    Args:
        src_path (Path): Validated source directory path to scan recursively.
        out_path (Path): Validated output directory path for extracted files.
        ai_file_path (Path): Validated AI context file path for consolidated output.
        extensions (List[str]): List of normalized file extensions to process.
        dry_run (bool): Whether to run in preview mode without writing files.
        verbose (bool): Whether to display detailed processing information.

    Raises:
        click.ClickException: If the extraction process encounters fatal errors.

    Note:
        Individual file processing errors are handled gracefully and do not
        stop the overall extraction process. Error details are collected and
        reported in the final summary.
    """
    try:
        if verbose:
            click.echo("Scanning for files...")

        # Find files to process using core extractor function
        files_to_process = extractor.find_files(src_path, extensions)

        if verbose:
            click.echo(f"Found {len(files_to_process)} files to process")
            for file_path in files_to_process:
                click.echo(f"  - {file_path.relative_to(src_path)}")
            click.echo()

        if not files_to_process:
            click.echo("No files found matching the specified extensions.")
            click.echo(f"Searched in: {src_path}")
            click.echo(f"Extensions: {', '.join(extensions)}")
            return

        # Process files and collect results
        all_metadata = []
        processed_files = 0
        skipped_files = 0
        error_files = []

        for file_path in files_to_process:
            try:
                if verbose:
                    click.echo(f"Processing: {file_path.relative_to(src_path)}")

                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract TikZ blocks using core extractor function
                tikz_blocks = extractor.extract_tikz_from_text(content)

                if tikz_blocks:
                    if dry_run:
                        # In dry-run mode, simulate the metadata creation
                        metadata = _simulate_block_metadata(
                            tikz_blocks, file_path, out_path
                        )
                    else:
                        # Actually write the blocks using core extractor function
                        metadata = extractor.write_extracted_blocks(
                            tikz_blocks, file_path, out_path
                        )

                    all_metadata.extend(metadata)
                    processed_files += 1

                    if verbose:
                        click.echo(f"  Found {len(tikz_blocks)} TikZ block(s)")
                        for i, block_meta in enumerate(metadata, 1):
                            if dry_run:
                                click.echo(
                                    f"    Would create: {Path(block_meta['out_path']).name}"
                                )
                            else:
                                click.echo(
                                    f"    Created: {Path(block_meta['out_path']).name}"
                                )
                else:
                    if verbose:
                        click.echo("  No TikZ blocks found")

            except UnicodeDecodeError as e:
                skipped_files += 1
                error_files.append((file_path, f"Encoding error: {e}"))
                if verbose:
                    click.echo(f"  Skipped (encoding error): {e}")
                continue
            except (IOError, OSError) as e:
                skipped_files += 1
                error_files.append((file_path, f"File access error: {e}"))
                if verbose:
                    click.echo(f"  Skipped (file access error): {e}")
                continue
            except Exception as e:
                skipped_files += 1
                error_files.append((file_path, f"Unexpected error: {e}"))
                if verbose:
                    click.echo(f"  Skipped (unexpected error): {e}")
                continue

        # Display comprehensive summary with user feedback
        click.echo()
        _display_extraction_summary(
            processed_files,
            len(all_metadata),
            skipped_files,
            error_files,
            dry_run,
            verbose,
        )

        # Handle AI context file creation
        if all_metadata:
            if dry_run:
                click.echo(f"Would create AI context file: {ai_file_path}")
                if verbose:
                    click.echo(
                        f"  Would contain {len(all_metadata)} TikZ blocks from {processed_files} files"
                    )
            else:
                try:
                    extractor.build_ai_context(all_metadata, ai_file_path)
                    click.echo(f"Created AI context file: {ai_file_path}")
                    if verbose:
                        click.echo(
                            f"  Contains {len(all_metadata)} TikZ blocks from {processed_files} files"
                        )
                except (IOError, OSError) as e:
                    click.echo(
                        f"Warning: Failed to create AI context file: {e}", err=True
                    )
        else:
            if not dry_run:
                click.echo("No TikZ blocks found - no files created")

        # Provide actionable feedback to user
        if processed_files == 0 and skipped_files == 0:
            click.echo("\nSuggestions:")
            click.echo(
                "- Check if the source directory contains files with the specified extensions"
            )
            click.echo("- Try different file extensions with --ext option")
            click.echo("- Use --verbose flag to see detailed processing information")
        elif processed_files == 0 and skipped_files > 0:
            click.echo("\nAll files were skipped due to errors.")
            click.echo("Use --verbose flag to see detailed error information.")
        elif len(all_metadata) == 0 and processed_files > 0:
            click.echo(f"\nProcessed {processed_files} files but found no TikZ blocks.")
            click.echo(
                "Make sure your files contain \\begin{tikzpicture}...\\end{tikzpicture} blocks."
            )

    except Exception as e:
        raise click.ClickException(f"Extraction failed: {e}")


def _display_extraction_summary(
    processed_files: int,
    total_blocks: int,
    skipped_files: int,
    error_files: List[Tuple[Path, str]],
    dry_run: bool,
    verbose: bool,
) -> None:
    """Display comprehensive extraction summary with user feedback.

    Provides a detailed summary of the extraction process including success
    metrics, error information, and actionable feedback for the user. The
    output format adapts based on dry-run mode and verbosity settings.

    Args:
        processed_files (int): Number of successfully processed files.
        total_blocks (int): Total number of TikZ blocks found and extracted.
        skipped_files (int): Number of files that were skipped due to errors.
        error_files (List[Tuple[Path, str]]): List of (file_path, error_message)
            tuples for files that encountered processing errors.
        dry_run (bool): Whether this was a dry run (affects output formatting).
        verbose (bool): Whether to show detailed error information.

    Note:
        The summary includes visual indicators (✓, ⚠) to help users quickly
        understand the results and provides suggestions for common issues.
    """
    if dry_run:
        click.echo("DRY RUN SUMMARY:")
        click.echo(f"Would process {processed_files} files")
        click.echo(f"Would extract {total_blocks} TikZ blocks")
        if skipped_files > 0:
            click.echo(f"Would skip {skipped_files} unreadable files")
    else:
        click.echo("EXTRACTION SUMMARY:")
        click.echo(f"Processed {processed_files} files")
        click.echo(f"Extracted {total_blocks} TikZ blocks")
        if skipped_files > 0:
            click.echo(f"Skipped {skipped_files} unreadable files")

    # Show error details if verbose and there were errors
    if verbose and error_files:
        click.echo("\nFile processing errors:")
        for file_path, error_msg in error_files:
            click.echo(f"  {file_path}: {error_msg}")

    # Provide success indicators
    if total_blocks > 0:
        click.echo(f"✓ Successfully found TikZ content in {processed_files} files")
    elif processed_files > 0:
        click.echo(
            f"✓ Successfully processed {processed_files} files (no TikZ blocks found)"
        )

    if skipped_files > 0:
        click.echo(f"⚠ {skipped_files} files could not be processed")
        if not verbose:
            click.echo("  Use --verbose to see error details")


def _simulate_block_metadata(
    blocks: List[str], src_path: Path, out_dir: Path
) -> List[Dict[str, any]]:
    """Simulate metadata creation for dry-run mode.

    Creates metadata structures identical to those that would be generated
    during actual file writing, but without performing any I/O operations.
    This allows dry-run mode to provide accurate previews of what would happen.

    Args:
        blocks (List[str]): List of TikZ block strings to simulate processing for.
        src_path (Path): Source file path where blocks were extracted from.
        out_dir (Path): Output directory path where files would be written.

    Returns:
        List[Dict[str, any]]: List of simulated metadata dictionaries with the
            same structure as real metadata, containing 'source', 'out_path',
            'index', and 'content' keys.

    Note:
        The generated metadata uses the same filename generation logic as the
        actual extraction process to ensure dry-run previews are accurate.
    """
    metadata = []
    sanitized_source = extractor.sanitize_name(src_path)

    for index, block in enumerate(blocks, 1):
        filename = f"{sanitized_source}__tikz{index}.tex"
        out_path = out_dir / filename

        block_metadata = {
            "source": str(src_path),
            "out_path": str(out_path),
            "index": index,
            "content": block,
        }
        metadata.append(block_metadata)

    return metadata


def _validate_source_path(src: Path) -> Path:
    """Validate and resolve source directory path.

    Args:
        src: Source path to validate

    Returns:
        Resolved absolute path

    Raises:
        click.ClickException: If path is invalid
    """
    try:
        resolved_path = src.resolve()
        if not resolved_path.exists():
            raise click.ClickException(f"Source directory does not exist: {src}")
        if not resolved_path.is_dir():
            raise click.ClickException(f"Source path is not a directory: {src}")
        return resolved_path
    except (OSError, RuntimeError) as e:
        raise click.ClickException(f"Invalid source path: {src} ({e})")


def _validate_output_path(out: Path) -> Path:
    """Validate and resolve output directory path.

    Args:
        out: Output path to validate

    Returns:
        Resolved absolute path

    Raises:
        click.ClickException: If path is invalid
    """
    try:
        resolved_path = out.resolve()
        # Check if parent directory exists and is writable
        parent = resolved_path.parent
        if not parent.exists():
            raise click.ClickException(f"Parent directory does not exist: {parent}")
        if not parent.is_dir():
            raise click.ClickException(f"Parent path is not a directory: {parent}")
        return resolved_path
    except (OSError, RuntimeError) as e:
        raise click.ClickException(f"Invalid output path: {out} ({e})")


def _validate_ai_file_path(ai_file: Path) -> Path:
    """Validate and resolve AI context file path.

    Args:
        ai_file: AI file path to validate

    Returns:
        Resolved absolute path

    Raises:
        click.ClickException: If path is invalid
    """
    try:
        resolved_path = ai_file.resolve()
        # Check if parent directory exists and is writable
        parent = resolved_path.parent
        if not parent.exists():
            raise click.ClickException(f"Parent directory does not exist: {parent}")
        if not parent.is_dir():
            raise click.ClickException(f"Parent path is not a directory: {parent}")
        return resolved_path
    except (OSError, RuntimeError) as e:
        raise click.ClickException(f"Invalid AI file path: {ai_file} ({e})")


def _parse_extensions(ext_string: str) -> List[str]:
    """Parse comma-separated extension list and validate format.

    Args:
        ext_string: Comma-separated string of file extensions

    Returns:
        List of normalized extensions (with leading dots)

    Raises:
        click.ClickException: If extensions are invalid
    """
    if not ext_string.strip():
        raise click.ClickException("Extension list cannot be empty")

    # Split by comma and clean up whitespace
    raw_extensions = [ext.strip() for ext in ext_string.split(",")]

    # Filter out empty strings
    raw_extensions = [ext for ext in raw_extensions if ext]

    if not raw_extensions:
        raise click.ClickException("No valid extensions found in extension list")

    # Normalize extensions (ensure they start with a dot)
    normalized_extensions = []
    for ext in raw_extensions:
        if not ext.startswith("."):
            normalized_extensions.append("." + ext)
        else:
            normalized_extensions.append(ext)

    # Validate extension format (basic check for reasonable file extensions)
    for ext in normalized_extensions:
        if len(ext) < 2:  # At least dot + one character
            raise click.ClickException(f"Invalid extension format: {ext}")
        if not ext[1:].replace("_", "").replace("-", "").isalnum():
            raise click.ClickException(f"Extension contains invalid characters: {ext}")

    return normalized_extensions


def main():
    """Entry point for the CLI command."""
    cli()


if __name__ == "__main__":
    main()
