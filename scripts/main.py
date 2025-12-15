#################################################
#  MODULE DESCRIPTION
#################################################

"""
Automates GitHub issue management by:
1. Validating issue templates.
2. Detecting duplicate issues based on title similarity.
3. Assigning issues to available contributors.
4. Commenting on issues with appropriate messages.

Uses GitHub API for interactions and Jinja2 for templating.

Authors: Dtar380
"""

#################################################
#  Importing MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
import os
import random
import json
from typing import Any

# EXTERNAL MODULES
import requests  # type: ignore
from rapidfuzz import fuzz
from jinja2 import Environment, FileSystemLoader, select_autoescape


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

USER_TEMPLATES_DIR = os.environ.get(
    "TEMPLATES_DIR", None
)  # User-defined templates directory
DEFAULT_TEMPLATES_DIR = os.path.join(
    os.environ.get("GITHUB_ACTION_PATH", ""), "templates"
)  # Default templates directory

EVENT_PATH = os.environ.get(
    "GITHUB_EVENT_PATH", None
)  # Path to GitHub event payload

# HEADERS FOR API REQUESTS
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


#  FUNCTIONS
#  ACTIONS
def close_issue(issue_number: int) -> None:
    """
    Closes a GitHub issue by a given issue number.

    :param issue_number: Number of the issue to be closed.
    :type issue_number: int
    """

    payload = json.dumps({"state": "closed"})
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

    payload = json.dumps({"body": comment})
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

    payload = json.dumps({"assignees": assignees})
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


#  VERIFICATIONS
def check_template(issue: dict[str, Any]) -> bool:
    """
    Checks if a GitHub issue follows a predefined template.

    :param issue: GitHub issue details.
    :type issue: dict[str, Any]
    :return: True if the issue follows the template, False otherwise.
    :rtype: bool
    """

    try:
        if "<!-- TEMPLATE" not in issue["body"] and not issue["labels"]:
            return False
        return True
    except requests.exceptions.Timeout:
        print(
            "ERROR: Request timed out while trying to fetch the issue details."
        )
        return False
    except requests.exceptions.RequestException as e:
        print(
            f"ERROR: An error occurred while trying to fetch the issue details: {e}"
        )
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return False


def check_duplicate(
    issue: dict[str, Any], threshold: int
) -> dict[str, list[Any]]:
    """
    Checks for duplicate GitHub issues based on title similarity.

    :param issue: GitHub issue details.
    :type issue: dict[str, Any]
    :param threshold: Similarity threshold (0-100) for considering issues as duplicates.
    :type threshold: int
    :return: Dictionary with lists of open and closed duplicate issues.
    :rtype: dict[str, list[Any]]
    """

    return_statement: dict[str, list[Any]] = {
        "open_duplicates": [],
        "closed_duplicates": [],
    }

    issue_title = issue.get("title", "")
    if not issue_title:
        raise ValueError("ERROR: Issue title is missing.")

    issue_number = issue.get("number", 0)
    if not issue_number:
        raise ValueError("ERROR: Issue number is missing.")

    query = f'repo:{REPO} is:issue "{issue_title}"'
    try:
        resp = requests.get(
            f"{API}search/issues",
            headers=HEADERS,
            params={"q": query},
            timeout=10,
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        print(
            "ERROR: Request timed out while trying to search for duplicate issues."
        )
        return return_statement
    except requests.exceptions.RequestException as e:
        print(
            f"ERROR: An error occurred while trying to search for duplicate issues: {e}"
        )
        return return_statement
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return return_statement

    results = resp.json().get("items", [])

    open_duplicates = []
    closed_duplicates = []

    for result in results:
        if result.get("number", 0) == issue_number:
            continue
        if fuzz.ratio(issue_title, result.get("title", "")) > threshold:
            if result.get("state", "") == "open":
                open_duplicates.append(result)
            else:
                closed_duplicates.append(result)

    return_statement["open_duplicates"] = open_duplicates
    return_statement["closed_duplicates"] = closed_duplicates

    return return_statement


#  HELPERS
def get_issue_number(event_path: str) -> int:
    """
    Retrieves the issue number from the GitHub event payload.

    :param event_path: Path to the GitHub event JSON file.
    :type event_path: str
    :return: Issue number.
    :rtype: int
    """

    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
    return event_data["issue"]["number"]


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


def get_contributors() -> list[str]:
    """
    Fetches the list of contributors for the repository.

    :return: List of contributor usernames.
    :rtype: list[str]
    """

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

    contributors = get_contributors()
    if not contributors:
        return []
    assignees: list[str] = []
    for contributor in contributors:
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
    if len(assignees) < k:
        return assignees
    return random.sample(assignees, k)


def render_template(template_path: str, template_name: str, **variables) -> str:
    """
    Renders a Jinja2 template with the provided variables.

    :param template_path: Path to the directory containing the templates.
    :type template_path: str
    :param template_name: Name of the template file (without extension).
    :type template_name: str
    :param variables: Variables to be passed to the template.
    :type variables: dict[str, Any]
    :return: Rendered template as a string.
    :rtype: str
    """

    if not os.path.isdir(template_path):
        raise FileNotFoundError("ERROR: Templates directory not found.")

    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape(["md"]),
    )

    try:
        template = env.get_template(f"{template_name}.j2")
        return template.render(**variables)
    except Exception as e:
        print(f"ERROR: An error occurred while rendering the template: {e}")
        return "Error rendering template. Please contact maintainers."


#  MAIN ENTRY POINT
def main() -> None:
    """
    Main function to automate GitHub issue management.

    1. Validates environment variables.
    2. Retrieves issue details from the GitHub event payload.
    3. Checks if the issue follows a predefined template.
    4. Checks for duplicate issues based on title similarity.
    5. Assigns the issue to available contributors.
    6. Comments on the issue with appropriate messages based on the checks.
    7. Closes the issue if it does not follow the template or is a duplicate
    """

    if API_TOKEN is None:
        raise ValueError("ERROR: Missing GITHUB_TOKEN environment variable.")
    if REPO is None:
        raise ValueError(
            "ERROR: Missing GITHUB_REPOSITORY environment variable."
        )
    if EVENT_PATH is None:
        raise ValueError(
            "ERROR: Missing GITHUB_EVENT_PATH environment variable."
        )

    issue_number = get_issue_number(EVENT_PATH)
    issue_details = get_issue_details(EVENT_PATH)

    if not check_template(issue_details):
        print("INFO: Issue does not follow template.")
        comment_issue(
            issue_number,
            render_template(
                USER_TEMPLATES_DIR or DEFAULT_TEMPLATES_DIR, "invalid_template"
            ),
        )
        close_issue(issue_number)
        return

    duplicates = check_duplicate(issue_details, threshold=DUPLICATE_THRESHOLD)
    if duplicates["open_duplicates"] or duplicates["closed_duplicates"]:
        print("INFO: Duplicate issues found.")
        comment_issue(
            issue_number,
            render_template(
                USER_TEMPLATES_DIR or DEFAULT_TEMPLATES_DIR,
                "duplicated",
                open_duplicates=duplicates["open_duplicates"],
                closed_duplicates=duplicates["closed_duplicates"],
            ),
        )
        close_issue(issue_number)
        return

    assignees = check_assignees(issue_number, k=2)
    if assignees:
        add_assignees(issue_number, assignees)
        print(f"INFO: Assigned issue to: {', '.join(assignees)}")
    else:
        print("INFO: No available contributors to assign the issue.")

    comment_issue(
        issue_number,
        render_template(
            USER_TEMPLATES_DIR or DEFAULT_TEMPLATES_DIR,
            "passed",
            assignees=assignees or [],
        ),
    )


#  RUNNING THE SCRIPT
if __name__ == "__main__":
    main()
