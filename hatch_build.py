"""Custom build hook for hatchling to embed git commit SHA.

This hook runs during the build process and writes the current git commit
SHA to a file that gets included in the built package.
"""

import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Build hook to embed git commit SHA in the package."""

    def initialize(self, version: str, build_data: dict) -> None:
        """Initialize the build hook."""
        # Get the git commit SHA
        commit_sha = self._get_git_commit()

        if commit_sha:
            # Write the commit SHA to a temporary file that will be included in the build
            # The build hook system will handle copying it to the build directory
            build_dir = Path(self.root) / "slash_commands"
            commit_file = build_dir / "_git_commit.py"

            content = f'''"""Git commit information embedded at build time."""

__git_commit__ = "{commit_sha}"
'''

            # Ensure the build directory exists
            build_dir.mkdir(exist_ok=True)

            with open(commit_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Ensure the file gets included in the build
            if "artifacts" not in build_data:
                build_data["artifacts"] = []

            build_data["artifacts"].append("slash_commands/_git_commit.py")

    def finalize(self, version: str, build_data: dict, artifact_path: str) -> None:
        """Clean up after build."""
        # Remove the generated file from source tree after build
        commit_file = Path(self.root) / "slash_commands" / "_git_commit.py"
        if commit_file.exists():
            commit_file.unlink()

    def _get_git_commit(self) -> str | None:
        """Get the short git commit SHA from the repository."""
        try:
            # Try to get the current git commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.root,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Not in a git repository or git not available
            return None


def get_build_hook():
    """Return the build hook instance."""
    return CustomBuildHook
