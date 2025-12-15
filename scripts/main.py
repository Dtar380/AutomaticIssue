import os
import json

import requests  # type: ignore


API = "https://api.github.com/"

API_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")
EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_issue_number(event_path: str) -> int:
    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
    return event_data["issue"]["number"]


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
        print(f"ERROR: An error occurred while trying to comment on the issue: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")


def main() -> None:
    if API_TOKEN is None:
        raise ValueError("ERROR: Missing GITHUB_TOKEN environment variable.")
    if REPO is None:
        raise ValueError("ERROR: Missing GITHUB_REPOSITORY environment variable.")
    if EVENT_PATH is None:
        raise ValueError("ERROR: Missing GITHUB_EVENT_PATH environment variable.")

    issue_number = get_issue_number(EVENT_PATH)
