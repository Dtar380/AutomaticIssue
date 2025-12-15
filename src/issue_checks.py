#################################################
#  MODULE DESCRIPTION
#################################################
"""
This module contains functions to check if GitHub issues meet certain criteria.
"""

#################################################
#  Importing MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
import re
from typing import Any

# EXTERNAL MODULES
from rapidfuzz import fuzz
import requests  # type: ignore

# LOCAL MODULES
from .config import API, HEADERS, REPO


#################################################
#  CODE
#################################################
def check_template(issue: dict[str, Any]) -> bool:
    """
    Checks if a GitHub issue follows a predefined template.

    :param issue: GitHub issue details.
    :type issue: dict[str, Any]
    :return: True if the issue follows the template, False otherwise.
    :rtype: bool
    """

    # Check for template markers in the issue body or presence of labels
    try:
        if "<!-- TEMPLATE" not in issue["body"] and not issue["labels"]:
            return False
        return True
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        return False


def normalize(issue_body: str) -> str:
    """
    Normalizes the issue body text for similarity comparison.

    :param issue_body: GitHub issue body text.
    :type issue_body: str
    :return: Normalized issue body text.
    :rtype: str
    """

    # Remove markdown, code blocks, URLs, and non-alphanumeric characters
    lines = []
    for line in issue_body.splitlines():
        line = line.strip()
        if not (
            not line
            or line.startswith("<!--")
            or line.startswith("###")
            or line.startswith("```")
        ):
            lines.append(line)
    text = " ".join(lines).lower()
    text = re.sub(r"`{3}.*?`{3}", "", text, flags=re.S)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\W+", " ", text)
    return text.strip()


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

    # Initialize return structure
    return_statement: dict[str, list[Any]] = {
        "open_duplicates": [],
        "closed_duplicates": [],
    }

    # Validate issue data
    issue_title = issue.get("title", "")
    if not issue_title:
        raise ValueError("ERROR: Issue title is missing.")

    issue_number = issue.get("number", 0)
    if not issue_number:
        raise ValueError("ERROR: Issue number is missing.")

    # Search for potential duplicate issues using GitHub API
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

    # Process search results
    results = resp.json().get("items", [])

    open_duplicates = []
    closed_duplicates = []

    # Analyze each result for similarity
    for result in results:
        # Skip the same issue
        if result.get("number", 0) == issue_number:
            continue
        title_score = fuzz.token_set_ratio(
            issue_title, result.get("title", "")
        )  # Get title similarity score

        if title_score < 66:
            continue  # Skip if below minimum title similarity

        body_score = fuzz.partial_ratio(
            normalize(issue.get("body", "")),
            normalize(result.get("body", "")),
        )  # Get body similarity score

        # Calculate overall similarity score
        overall_score = 0.7 * title_score + 0.3 * body_score

        # Check against threshold and categorize
        if overall_score >= threshold:
            if result.get("state", "") == "open":
                open_duplicates.append(result)
            else:
                closed_duplicates.append(result)

    # Populate return structure
    return_statement["open_duplicates"] = open_duplicates
    return_statement["closed_duplicates"] = closed_duplicates

    return return_statement
