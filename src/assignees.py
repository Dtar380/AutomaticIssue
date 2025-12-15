#################################################
#  MODULE DESCRIPTION
#################################################
"""
This module contains functions to manage assignees for GitHub issues.
"""

#################################################
#  Importing MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
import random

# EXTERNAL MODULES
import requests  # type: ignore

# LOCAL MODULES
from .config import API, HEADERS, REPO


#################################################
#  CODE
#################################################
def get_contributors() -> list[str]:
    """
    Fetches the list of contributors for the repository.

    :return: List of contributor usernames.
    :rtype: list[str]
    """

    # Make the GET request to fetch contributors
    try:
        response = requests.get(
            f"{API}repos/{REPO}/contributors",
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        return [
            collaborator.get("login", "") for collaborator in response.json()
        ]
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out while trying to fetch contributors.")
        return []
    except requests.exceptions.RequestException as e:
        print(
            f"ERROR: An error occurred while trying to fetch contributors: {e}"
        )
        return []
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return []


def check_assignees(issue_number: int, k: int) -> list[str]:
    """
    Checks and returns a list of available assignees for a GitHub issue.

    :param issue_number: Number of the issue to check assignees for.
    :type issue_number: int
    :param k: Number of assignees to return.
    :type k: int
    :return: List of available assignees.
    :rtype: list[str]
    """

    # Fetch the list of contributors
    contributors = get_contributors()
    if not contributors:
        return []

    # Check which contributors are already assigned to the issue
    assignees: list[str] = []
    for contributor in contributors:

        # Make the GET request to check if the contributor is an assignable
        try:
            response = requests.get(
                f"{API}repos/{REPO}/issues/{issue_number}/assignees/{contributor}",
                headers=HEADERS,
                timeout=10,
            )
            if response.status_code == 204:
                assignees.append(contributor)
        except requests.exceptions.Timeout:
            print(
                "ERROR: Request timed out while trying to check assignees for the issue."
            )
            continue
        except requests.exceptions.RequestException as e:
            print(
                f"ERROR: An error occurred while trying to check assignees for the issue: {e}"
            )
            continue
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {e}")
            continue

    # Return k random assignees from the available list
    if len(assignees) < k:
        return assignees
    return random.sample(assignees, k)
