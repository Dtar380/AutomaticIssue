#################################################
#  MODULE DESCRIPTION
#################################################
"""
This module contains functions to interact with GitHub issues via the GitHub API.
It provides functionalities to close issues, comment on issues, and add assignees to issues.
"""

#################################################
#  Importing MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
import json

# EXTERNAL MODULES
import requests  # type: ignore

# LOCAL MODULES
from .config import API, REPO, HEADERS


#################################################
#  CODE
#################################################
def close_issue(issue_number: int) -> None:
    """
    Closes a GitHub issue by a given issue number.

    :param issue_number: Number of the issue to be closed.
    :type issue_number: int
    """

    # Prepare the payload to close the issue
    payload = json.dumps({"state": "closed"})

    # Make the PATCH request to close the issue
    try:
        requests.patch(
            f"{API}repos/{REPO}/issues/{issue_number}",
            headers=HEADERS,
            data=payload,
            timeout=10,
        )
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out while trying to close the issue.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: An error occurred while trying to close the issue: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")


def comment_issue(issue_number: int, comment: str) -> None:
    """
    Adds a comment to a GitHub issue by a given issue number.

    :param issue_number: Number of the issue to be commented on.
    :type issue_number: int
    :param comment: Content of the comment to be added.
    :type comment: str
    """

    # Prepare the payload with the comment body
    payload = json.dumps({"body": comment})

    # Make the POST request to add the comment
    try:
        requests.post(
            f"{API}repos/{REPO}/issues/{issue_number}/comments",
            headers=HEADERS,
            data=payload,
            timeout=10,
        )
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out while trying to comment on the issue.")
    except requests.exceptions.RequestException as e:
        print(
            f"ERROR: An error occurred while trying to comment on the issue: {e}"
        )
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")


def add_assignees(issue_number: int, assignees: list[str]) -> None:
    """
    Adds assignees to a GitHub issue by a given issue number.

    :param issue_number: Number of the issue to add assignees to.
    :type issue_number: int
    :param assignees: List of assignees to be added to the issue.
    :type assignees: list[str]
    """

    # Prepare the payload with the assignees
    payload = json.dumps({"assignees": assignees})

    # Make the POST request to add the assignees
    try:
        requests.post(
            f"{API}repos/{REPO}/issues/{issue_number}/assignees",
            headers=HEADERS,
            data=payload,
            timeout=10,
        )
    except requests.exceptions.Timeout:
        print(
            "ERROR: Request timed out while trying to add assignees to the issue."
        )
    except requests.exceptions.RequestException as e:
        print(
            f"ERROR: An error occurred while trying to add assignees to the issue: {e}"
        )
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
