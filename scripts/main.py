#################################################
#  Importing MODULES
#################################################
from __future__ import annotations

import os
import random
import json
from typing import Any

import requests  # type: ignore
from rapidfuzz import fuzz
from jinja2 import Environment, FileSystemLoader, select_autoescape


#################################################
#  CODE
#################################################
#  GLOBAL VARIABLES
API = "https://api.github.com/"

API_TOKEN = os.environ.get("GITHUB_TOKEN", None)
REPO = os.environ.get("GITHUB_REPOSITORY", None)

DUPLICATE_THRESHOLD = int(os.environ.get("DUPLICATE_THRESHOLD", 80))

USER_TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", None)
DEFAULT_TEMPLATES_DIR = os.path.join(
    os.environ.get("GITHUB_ACTION_PATH", ""), "templates"
)

EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH", None)


HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


#  FUNCTIONS
#  ACTIONS
def close_issue(issue_number: int) -> None:
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


def add_assignees(issue_number: int, assignees: list[Any]) -> None:
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
def get_contributors() -> list[str]:
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


def get_issue_number(event_path: str) -> int:
    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
    return event_data["issue"]["number"]


def get_issue_details(event_path: str) -> dict[str, Any]:
    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
    return event_data["issue"]


def render_template(template_path: str, template_name: str, **variables) -> str:
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
