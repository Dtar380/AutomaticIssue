#################################################
#  MODULE DESCRIPTION
#################################################
"""
This module contains functions to retrieve GitHub issue details from the event payload.
"""

################################################
#  Importing MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
import json
from typing import Any


#################################################
#  CODE
#################################################
def get_issue_details(event_path: str) -> dict[str, Any]:
    """
    Retrieves the issue details from the GitHub event payload.

    :param event_path: Path to the GitHub event JSON file.
    :type event_path: str
    :return: Issue details.
    :rtype: dict[str, Any]
    """

    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
    return event_data["issue"]
