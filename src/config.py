#################################################
#  MODULE DESCRIPTION
#################################################
"""
This module contains configuration settings for the GitHub Issue Automation tool.
It defines constants and environment variable retrievals necessary for the code operation.
"""

#################################################
#  IMPORTING MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
import os
from pathlib import Path

#################################################
#  CODE
#################################################
#  GLOBAL VARIABLES
# CONSTANTS
API = "https://api.github.com/"  # GitHub API base URL

# ENVIRONMENT VARIABLES
API_TOKEN = os.environ.get("GITHUB_TOKEN", None)  # GitHub API token
REPO = os.environ.get("GITHUB_REPOSITORY", None)  # Repository name

DUPLICATE_THRESHOLD = int(
    os.environ.get("DUPLICATE_THRESHOLD", 80)
)  # Similarity threshold

USER_TEMPLATES_DIR: Path | None = (
    Path(os.environ.get("TEMPLATES_DIR", ""))
    if os.environ.get("TEMPLATES_DIR", None) is not None
    else None
)  # User-defined templates directory
DEFAULT_TEMPLATES_DIR: Path = Path(
    os.path.join(os.environ.get("GITHUB_ACTION_PATH", ""), "templates")
)  # Default templates directory

TEMPLATES_DIR = USER_TEMPLATES_DIR or DEFAULT_TEMPLATES_DIR

EVENT_PATH = os.environ.get(
    "GITHUB_EVENT_PATH", None
)  # Path to GitHub event payload

# HEADERS FOR API REQUESTS
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}
