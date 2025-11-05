"""Writer for generating slash commands for multiple agents."""

from __future__ import annotations

import importlib.resources
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import questionary
import tomllib
import yaml

from mcp_server.prompt_utils import (
    MarkdownPrompt,
    create_markdown_prompt_with_source,
    load_markdown_prompt,
)
from slash_commands.config import AgentConfig, get_agent_config, list_agent_keys
from slash_commands.generators import CommandGenerator
from slash_commands.github_utils import (
    GitHubRepoError,
    download_github_prompts,
    get_github_repo_info,
    parse_github_url,
)


def _find_package_prompts_dir() -> Path | None:
    """Find the prompts directory in the installed package.

    Returns:
        Path to prompts directory if found, None otherwise
    """
    # Try to use importlib.resources to locate bundled prompts
    # This works for installed packages (including wheel distributions)
    try:
        # Get a traversable for a known package in our distribution
        package_anchor = importlib.resources.files("slash_commands")
        # Navigate from the package anchor to the included "prompts" directory
        prompts_resource = package_anchor.parent / "prompts"
        # Check if the prompts directory exists in the resource
        if prompts_resource.is_dir():
            return Path(str(prompts_resource))
    except (ModuleNotFoundError, AttributeError, ValueError):
        # Fall through to fallback strategy
        pass

    # Fallback strategy: use file path resolution
    # The prompts directory is force-included at the package root level
    # When installed, the structure is:
    #   package_root/
    #     __version__.py
    #     prompts/
    #     slash_commands/
    #       writer.py
    #
    # So we need to go up from writer.py to the package root
    package_root = Path(__file__).parent.parent
    prompts_dir = package_root / "prompts"

    if prompts_dir.exists():
        return prompts_dir

    return None


OverwriteAction = Literal["cancel", "overwrite", "backup", "overwrite-all"]


def prompt_overwrite_action(file_path: Path) -> OverwriteAction:
    """Prompt user for what to do with an existing file.

    Args:
        file_path: Path to the existing file

    Returns:
        One of: "cancel", "overwrite", "backup", "overwrite-all"
    """
    response = questionary.select(
        f"File already exists: {file_path}\nWhat would you like to do?",
        choices=[
            questionary.Choice("Cancel", "cancel"),
            questionary.Choice("Overwrite this file", "overwrite"),
            questionary.Choice("Create backup and overwrite", "backup"),
            questionary.Choice("Overwrite all existing files", "overwrite-all"),
        ],
    ).ask()

    if response is None:
        # User pressed Ctrl+C or similar
        return "cancel"

    return response  # type: ignore[return-value]


def create_backup(file_path: Path) -> Path:
    """Create a timestamped backup of an existing file.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the backup file
    """
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}.bak")

    # Copy file with metadata preserved
    shutil.copy2(file_path, backup_path)

    return backup_path


class SlashCommandWriter:
    """Orchestrates prompt loading and generation of command files for multiple agents."""

    def __init__(  # noqa: PLR0913
        self,
        prompts_dir: Path,
        agents: list[str] | None = None,
        dry_run: bool = False,
        base_path: Path | None = None,
        overwrite_action: OverwriteAction | None = None,
        is_explicit_prompts_dir: bool = True,
        github_url: str | None = None,
    ):
        """Initialize the writer.

        Args:
            prompts_dir: Directory containing prompt files (ignored if github_url is provided)
            agents: List of agent keys to generate commands for. If None, uses all supported agents.
            dry_run: If True, don't write files but report what would be written
            base_path: Base directory for output paths. If None, uses current directory.
            overwrite_action: Global overwrite action to apply. If None, will prompt per file.
            is_explicit_prompts_dir: If True, prompts_dir was explicitly provided by user.
                If False, use bundled prompts fallback.
            github_url: GitHub URL to download prompts from. If provided, prompts_dir is ignored.
        """
        self.prompts_dir = prompts_dir
        self.agents = agents if agents is not None else list_agent_keys()
        self.dry_run = dry_run
        self.base_path = base_path or Path.cwd()
        self.overwrite_action = overwrite_action
        self.is_explicit_prompts_dir = is_explicit_prompts_dir
        self.github_url = github_url
        self._global_overwrite = False  # Track if user chose "overwrite-all"
        self._backups_created = []  # Track backup files created

        # GitHub-specific attributes
        self.github_repo_info = None
        self.temp_dir = None
        self.download_progress = {"files_downloaded": 0, "total_files": 0}

        # If GitHub URL is provided, parse and validate it
        if self.github_url:
            self._init_github_source()

    def _init_github_source(self) -> None:
        """Initialize GitHub source by parsing URL and retrieving repo info."""
        try:
            # Parse GitHub URL
            parsed_url = parse_github_url(self.github_url)

            # Get repository info
            self.github_repo_info = get_github_repo_info(parsed_url["owner"], parsed_url["repo"])

            # Add parsed info to repo info
            self.github_repo_info.update(parsed_url)

        except GitHubRepoError as e:
            raise ValueError(f"Invalid GitHub repository: {e.message}") from e

    def generate(self) -> dict[str, Any]:
        """Generate command files for all configured agents.

        Returns:
            Dict with keys:
            - prompts_loaded: Number of prompts loaded
            - files_written: Number of files written
            - files: List of dicts with path and agent info
            - prompts: List of prompt metadata
        """
        # Load prompts
        prompts = self._load_prompts()

        # Get agent configs
        agent_configs = [get_agent_config(key) for key in self.agents]

        # Check for existing files upfront and prompt once if any exist
        if not self.dry_run and not self.overwrite_action:
            existing_files = self._find_existing_files(prompts, agent_configs)
            if existing_files:
                action = self._prompt_for_all_existing_files(existing_files)
                if action == "cancel":
                    raise RuntimeError("Cancelled by user")
                self.overwrite_action = action

        # Generate files
        files = []
        files_written = 0
        for prompt in prompts:
            for agent in agent_configs:
                file_info = self._generate_file(prompt, agent)
                if file_info:
                    files.append(file_info)
                    # Only count files that were actually written (not dry run)
                    if not self.dry_run:
                        files_written += 1

        return {
            "prompts_loaded": len(prompts),
            "files_written": files_written,
            "files": files,
            "prompts": [{"name": p.name, "path": str(p.path)} for p in prompts],
            "backups_created": self._backups_created,
        }

    def _load_prompts(self) -> list[MarkdownPrompt]:
        """Load all prompts from the prompts directory or GitHub repository."""
        # If GitHub URL is provided, download from GitHub
        if self.github_url:
            return self._load_prompts_from_github()

        # Original local directory logic
        prompts_dir = self.prompts_dir
        if not prompts_dir.exists():
            # Only attempt fallback to bundled prompts when using default path
            if not self.is_explicit_prompts_dir:
                # Try to find prompts in the installed package
                package_prompts_dir = _find_package_prompts_dir()
                if package_prompts_dir is not None:
                    prompts_dir = package_prompts_dir
                else:
                    raise ValueError(f"Prompts directory does not exist: {self.prompts_dir}")
            else:
                # Explicit path not found, raise error immediately without fallback
                raise ValueError(f"Prompts directory does not exist: {self.prompts_dir}")

        prompts = []
        for prompt_file in sorted(prompts_dir.glob("*.md")):
            base_prompt = load_markdown_prompt(prompt_file)
            # Add local source metadata
            prompt = create_markdown_prompt_with_source(
                base_prompt,
                source_type="local",
                source_local_path=str(prompts_dir),
                source_timestamp=datetime.now(UTC).isoformat(),
            )
            prompts.append(prompt)

        return prompts

    def _load_prompts_from_github(self) -> list[MarkdownPrompt]:
        """Load prompts from GitHub repository."""
        try:
            # Download prompts from GitHub
            parsed_url = parse_github_url(self.github_url)
            self.temp_dir = download_github_prompts(
                parsed_url["owner"], parsed_url["repo"], parsed_url["branch"], parsed_url["path"]
            )

            # Update progress
            files = list(self.temp_dir.glob("*.md"))
            self.download_progress = {"files_downloaded": len(files), "total_files": len(files)}

            # Load prompts from downloaded files
            prompts = []
            for prompt_file in sorted(self.temp_dir.glob("*.md")):
                base_prompt = load_markdown_prompt(prompt_file)
                # Add GitHub source metadata
                source_metadata = {
                    "source_type": "github",
                    "source_github_url": self.github_url,
                    "source_timestamp": datetime.now(UTC).isoformat(),
                }
                if self.github_repo_info:
                    source_metadata.update(
                        {
                            "source_github_owner": self.github_repo_info.get("owner"),
                            "source_github_repo": self.github_repo_info.get("name"),
                            "source_github_branch": parsed_url["branch"],
                            "source_github_path": parsed_url["path"],
                        }
                    )

                prompt = create_markdown_prompt_with_source(base_prompt, **source_metadata)
                prompts.append(prompt)

            return prompts

        except GitHubRepoError as e:
            raise ValueError(f"Failed to load prompts from GitHub: {e.message}") from e
        finally:
            # Clean up temporary directory if not in dry run mode
            if self.temp_dir and not self.dry_run:
                try:
                    shutil.rmtree(self.temp_dir)
                    self.temp_dir = None
                except Exception:
                    pass  # Ignore cleanup errors

    def _find_existing_files(
        self, prompts: list[MarkdownPrompt], agent_configs: list[AgentConfig]
    ) -> list[Path]:
        """Find all existing files that would be overwritten.

        Args:
            prompts: List of prompts to check
            agent_configs: List of agent configurations

        Returns:
            List of paths to existing files
        """
        existing_files = []
        for prompt in prompts:
            if not prompt.enabled:
                continue
            for agent in agent_configs:
                # Determine output path (same logic as _generate_file)
                safe_stem = Path(prompt.name).name
                safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", safe_stem).strip("-_.") or "command"
                filename = f"{safe_stem}{agent.command_file_extension}"
                output_path = self.base_path / agent.command_dir / filename

                if output_path.exists():
                    existing_files.append(output_path)
        return existing_files

    def _prompt_for_all_existing_files(self, existing_files: list[Path]) -> OverwriteAction:
        """Prompt user once for all existing files.

        Args:
            existing_files: List of paths to existing files

        Returns:
            OverwriteAction to apply to all existing files
        """
        file_count = len(existing_files)
        response = questionary.select(
            f"Found {file_count} existing file{'s' if file_count != 1 else ''} that will be overwritten.\nWhat would you like to do?",
            choices=[
                questionary.Choice("Cancel", "cancel"),
                questionary.Choice("Overwrite all existing files", "overwrite"),
                questionary.Choice("Create backups and overwrite all", "backup"),
            ],
        ).ask()

        if response is None:
            # User pressed Ctrl+C or similar
            return "cancel"

        return response  # type: ignore[return-value]

    def _generate_file(self, prompt: MarkdownPrompt, agent: AgentConfig) -> dict[str, Any] | None:
        """Generate a command file for a single prompt and agent.

        Args:
            prompt: The prompt to generate from
            agent: The agent configuration

        Returns:
            Dict with path and agent info, or None if skipped
        """
        # Skip if prompt is disabled
        if not prompt.enabled:
            return None

        # Create generator for this agent's format
        generator = CommandGenerator.create(agent.command_format)

        # Generate command content
        content = generator.generate(prompt, agent)

        # Determine output path (resolve relative to base_path)
        # Sanitize file stem: drop any path components and restrict to safe chars
        safe_stem = Path(prompt.name).name  # remove any directories
        safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", safe_stem).strip("-_.") or "command"
        filename = f"{safe_stem}{agent.command_file_extension}"
        output_path = self.base_path / agent.command_dir / filename

        # Handle existing files
        if output_path.exists() and not self.dry_run:
            action = self._handle_existing_file(output_path)
            if action == "cancel":
                raise RuntimeError("Cancelled by user")
            elif action == "backup":
                backup_path = create_backup(output_path)
                self._backups_created.append(str(backup_path))

        # Create parent directories if needed
        if not self.dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file if not dry run
        if not self.dry_run:
            output_path.write_text(content, encoding="utf-8")

        return {
            "path": str(output_path),
            "agent": agent.key,
            "agent_display_name": agent.display_name,
            "format": agent.command_format.value,
        }

    def _handle_existing_file(self, file_path: Path) -> OverwriteAction:
        """Handle an existing file by applying the global overwrite action.

        Args:
            file_path: Path to the existing file

        Returns:
            OverwriteAction to apply
        """
        # Use global action if set (it should always be set after our upfront check)
        if self.overwrite_action:
            return self.overwrite_action

        # This should not happen anymore, but keep as fallback
        return "overwrite"

    def find_generated_files(
        self, agents: list[str] | None = None, include_backups: bool = True
    ) -> list[dict[str, Any]]:
        """Find all files generated by this tool.

        Args:
            agents: List of agent keys to search. If None, searches all supported agents.
            include_backups: If True, includes backup files in the results.

        Returns:
            List of dicts with keys: path, agent, agent_display_name, type, reason
        """
        found_files = []
        agent_keys = list_agent_keys() if agents is None else agents

        for agent_key in agent_keys:
            try:
                agent = get_agent_config(agent_key)
                command_dir = self.base_path / agent.command_dir

                if not command_dir.exists():
                    continue

                # Check for regular command files
                for file_path in command_dir.glob(f"*{agent.command_file_extension}"):
                    if self._is_generated_file(file_path, agent):
                        # Convert Path to string explicitly using os.fspath
                        path_str = os.fspath(file_path)
                        found_files.append(
                            {
                                "path": path_str,
                                "agent": agent.key,
                                "agent_display_name": agent.display_name,
                                "type": "command",
                                "reason": "Has generated metadata",
                            }
                        )

                # Check for backup files
                if include_backups:
                    # Look for files matching the backup pattern: *.extension.timestamp.bak
                    escaped_ext = re.escape(agent.command_file_extension)
                    pattern = re.compile(rf".*{escaped_ext}\.\d{{8}}-\d{{6}}\.bak$")
                    for file_path in command_dir.iterdir():
                        if file_path.is_file() and pattern.match(file_path.name):
                            # Convert Path to string explicitly using os.fspath
                            path_str = os.fspath(file_path)
                            found_files.append(
                                {
                                    "path": path_str,
                                    "agent": agent.key,
                                    "agent_display_name": agent.display_name,
                                    "type": "backup",
                                    "reason": "Matches backup pattern",
                                }
                            )
            except KeyError:
                # Agent key not found, skip
                continue

        return found_files

    def _is_generated_file(self, file_path: Path, agent: AgentConfig) -> bool:
        """Check if a file was generated by this tool.

        Args:
            file_path: Path to the file to check
            agent: Agent configuration

        Returns:
            True if the file was generated by this tool
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False

        if agent.command_format.value == "markdown":
            return self._is_generated_markdown(content)
        elif agent.command_format.value == "toml":
            return self._is_generated_toml(content)
        return False

    def _is_generated_markdown(self, content: str) -> bool:
        """Check if markdown content was generated by this tool.

        Args:
            content: File content

        Returns:
            True if generated by this tool
        """
        # Check for YAML frontmatter with metadata
        if not content.startswith("---"):
            return False

        try:
            # Extract YAML frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                return False

            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                return False

            # Check for meta section with source_prompt or version
            meta = frontmatter.get("meta", {})
            return isinstance(meta, dict) and ("source_prompt" in meta or "version" in meta)
        except (yaml.YAMLError, AttributeError):
            return False

    def _is_generated_toml(self, content: str) -> bool:
        """Check if TOML content was generated by this tool.

        Args:
            content: File content

        Returns:
            True if generated by this tool
        """
        try:
            data = tomllib.loads(content)
            if not isinstance(data, dict):
                return False

            # Check for meta section with source_prompt or version
            meta = data.get("meta", {})
            return isinstance(meta, dict) and ("source_prompt" in meta or "version" in meta)
        except tomllib.TOMLDecodeError:
            return False

    def cleanup(
        self, agents: list[str] | None = None, include_backups: bool = True, dry_run: bool = False
    ) -> dict[str, Any]:
        """Clean up generated files.

        Args:
            agents: List of agent keys to clean. If None, cleans all agents.
            include_backups: If True, includes backup files in cleanup.
            dry_run: If True, don't delete files but report what would be deleted.

        Returns:
            Dict with keys: files_found, files_deleted, files
        """
        found_files = self.find_generated_files(agents=agents, include_backups=include_backups)

        deleted_files = []
        errors = []

        for file_info in found_files:
            file_path = Path(file_info["path"])
            if not dry_run:
                try:
                    file_path.unlink()
                    deleted_files.append(file_info)
                except OSError as e:
                    errors.append({"path": str(file_path), "error": str(e)})
            else:
                deleted_files.append(file_info)

        return {
            "files_found": len(found_files),
            "files_deleted": len(deleted_files),
            "files": deleted_files,
            "errors": errors,
        }
