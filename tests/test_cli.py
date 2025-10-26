"""CLI integration tests for tikz_extractor.cli module."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from tikz_extractor.cli import cli


class TestCliBasicFunctionality:
    """Test basic CLI functionality and argument parsing."""

    def test_cli_help(self):
        """Test that CLI help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Extract TikZ picture environments from codebases" in result.output
        assert "--src" in result.output
        assert "--out" in result.output
        assert "--ext" in result.output
        assert "--ai-file" in result.output
        assert "--dry-run" in result.output
        assert "--verbose" in result.output

    def test_cli_default_parameters(self, test_file_structure):
        """Test CLI with default parameters."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Copy test files to current directory
            for file_path in test_file_structure.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(test_file_structure)
                    target_path = Path(rel_path)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text(
                        file_path.read_text(encoding="utf-8"), encoding="utf-8"
                    )

            result = runner.invoke(cli)

            assert result.exit_code == 0

            # Check that default output directory was created
            assert Path("tikz").exists()

            # Check that AI context file was created
            assert Path("ai_context.txt").exists()

    def test_cli_custom_source_directory(self, test_file_structure):
        """Test CLI with custom source directory."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--out", "custom_output"]
            )

            assert result.exit_code == 0
            assert Path("custom_output").exists()

    def test_cli_custom_extensions(self, test_file_structure):
        """Test CLI with custom file extensions."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--ext", ".tex,.md"]
            )

            assert result.exit_code == 0
            # Should process .tex and .md files but not .py files


class TestCliDryRunMode:
    """Test CLI dry-run functionality."""

    def test_cli_dry_run_basic(self, test_file_structure):
        """Test basic dry-run functionality."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--dry-run"]
            )

            assert result.exit_code == 0
            assert "DRY RUN SUMMARY:" in result.output
            assert "Would process" in result.output
            assert "Would extract" in result.output

            # No files should be created in dry-run mode
            assert not Path("tikz").exists()
            assert not Path("ai_context.txt").exists()

    def test_cli_dry_run_with_verbose(self, test_file_structure):
        """Test dry-run with verbose output."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--dry-run", "--verbose"]
            )

            assert result.exit_code == 0
            assert "DRY RUN SUMMARY:" in result.output
            assert "Source directory:" in result.output
            assert "Output directory:" in result.output
            assert "Would create:" in result.output

    def test_cli_dry_run_shows_would_create_files(self, test_file_structure):
        """Test that dry-run shows what files would be created."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--dry-run", "--verbose"]
            )

            assert result.exit_code == 0
            assert "Would create:" in result.output
            assert "__tikz" in result.output  # Should show tikz file naming pattern


class TestCliVerboseMode:
    """Test CLI verbose functionality."""

    def test_cli_verbose_basic(self, test_file_structure):
        """Test basic verbose functionality."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--verbose"]
            )

            assert result.exit_code == 0
            assert "Source directory:" in result.output
            assert "Output directory:" in result.output
            assert "File extensions:" in result.output
            assert "Scanning for files..." in result.output
            assert "Processing:" in result.output

    def test_cli_verbose_shows_file_processing(self, test_file_structure):
        """Test that verbose mode shows individual file processing."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--verbose"]
            )

            assert result.exit_code == 0
            assert "Found" in result.output and "files to process" in result.output
            assert "Processing:" in result.output
            assert "Found" in result.output and "TikZ block" in result.output

    def test_cli_verbose_shows_summary_details(self, test_file_structure):
        """Test that verbose mode shows detailed summary."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(test_file_structure), "--verbose"]
            )

            assert result.exit_code == 0
            assert "EXTRACTION SUMMARY:" in result.output
            assert "Processed" in result.output
            assert "Extracted" in result.output


class TestCliErrorHandling:
    """Test CLI error handling and validation."""

    def test_cli_invalid_source_directory(self):
        """Test CLI with non-existent source directory."""
        runner = CliRunner()

        result = runner.invoke(cli, ["--src", "/nonexistent/directory"])

        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_cli_source_is_file_not_directory(self, temp_dir):
        """Test CLI when source path is a file, not a directory."""
        runner = CliRunner()

        # Create a file instead of directory
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content", encoding="utf-8")

        result = runner.invoke(cli, ["--src", str(test_file)])

        assert result.exit_code != 0
        assert "is a file" in result.output

    def test_cli_invalid_output_parent_directory(self, test_file_structure):
        """Test CLI with invalid output directory parent."""
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ["--src", str(test_file_structure), "--out", "/nonexistent/parent/output"],
        )

        assert result.exit_code != 0
        assert "Parent directory does not exist" in result.output

    def test_cli_empty_extensions_list(self, test_file_structure):
        """Test CLI with empty extensions list."""
        runner = CliRunner()

        result = runner.invoke(cli, ["--src", str(test_file_structure), "--ext", ""])

        assert result.exit_code != 0
        assert "cannot be empty" in result.output

    def test_cli_invalid_extension_format(self, test_file_structure):
        """Test CLI with invalid extension format."""
        runner = CliRunner()

        result = runner.invoke(
            cli, ["--src", str(test_file_structure), "--ext", ".tex,invalid@ext"]
        )

        assert result.exit_code != 0
        assert "invalid characters" in result.output


class TestCliOutputAndFeedback:
    """Test CLI output and user feedback."""

    def test_cli_success_feedback(self, test_file_structure):
        """Test that CLI provides success feedback."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--src", str(test_file_structure)])

            assert result.exit_code == 0
            assert "EXTRACTION SUMMARY:" in result.output
            assert (
                "Successfully found TikZ content" in result.output
                or "Successfully processed" in result.output
            )
            assert "Created AI context file:" in result.output

    def test_cli_no_tikz_found_feedback(self, temp_dir):
        """Test CLI feedback when no TikZ blocks are found."""
        runner = CliRunner()

        # Create files without TikZ content
        (temp_dir / "no_tikz.tex").write_text("No TikZ here", encoding="utf-8")

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--src", str(temp_dir)])

            assert result.exit_code == 0
            assert "No TikZ blocks found" in result.output

    def test_cli_no_files_found_feedback(self, temp_dir):
        """Test CLI feedback when no matching files are found."""
        runner = CliRunner()

        # Create files with non-matching extensions
        (temp_dir / "test.txt").write_text("Text file", encoding="utf-8")

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--src", str(temp_dir), "--ext", ".tex"])

            assert result.exit_code == 0
            assert "No files found matching the specified extensions" in result.output

    def test_cli_suggestions_for_no_results(self, temp_dir):
        """Test that CLI provides helpful suggestions when no results found."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["--src", str(temp_dir), "--ext", ".nonexistent"]
            )

            assert result.exit_code == 0
            assert "No files found matching the specified extensions" in result.output


class TestCliParameterCombinations:
    """Test various CLI parameter combinations."""

    def test_cli_all_parameters_custom(self, test_file_structure):
        """Test CLI with all custom parameters."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--src",
                    str(test_file_structure),
                    "--out",
                    "custom_tikz",
                    "--ext",
                    ".tex,.md",
                    "--ai-file",
                    "custom_ai.txt",
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert Path("custom_tikz").exists()
            assert Path("custom_ai.txt").exists()

    def test_cli_short_flags(self, test_file_structure):
        """Test CLI with short flag versions."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "-s",
                    str(test_file_structure),
                    "-o",
                    "short_output",
                    "-e",
                    ".tex",
                    "-a",
                    "short_ai.txt",
                    "-v",
                ],
            )

            assert result.exit_code == 0
            assert Path("short_output").exists()
            assert Path("short_ai.txt").exists()

    def test_cli_dry_run_with_all_options(self, test_file_structure):
        """Test dry-run mode with all options."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "--src",
                    str(test_file_structure),
                    "--out",
                    "test_output",
                    "--ext",
                    ".tex,.md,.py",
                    "--ai-file",
                    "test_ai.txt",
                    "--dry-run",
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "DRY RUN SUMMARY:" in result.output
            assert "Would create AI context file:" in result.output

            # No files should be created
            assert not Path("test_output").exists()
            assert not Path("test_ai.txt").exists()
