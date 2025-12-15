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

# LOCAL MODULES
from src.config import (
    API_TOKEN,
    EVENT_PATH,
    REPO,
    DEFAULT_TEMPLATES_DIR,
    USER_TEMPLATES_DIR,
    DUPLICATE_THRESHOLD,
)
from src.event import get_issue_details
from src.issue_checks import check_template, check_duplicate
from src.assignees import check_assignees
from src.templates import render_template
from src.github_api import comment_issue, close_issue, add_assignees


#################################################
#  CODE
#################################################
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

    # Validate essential environment variables
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

    # Retrieve issue details from the GitHub event payload
    issue = get_issue_details(EVENT_PATH)
    issue_number = issue.get("number", 0)

    # Check if the issue follows a predefined template
    if not check_template(issue):
        print("INFO: Issue does not follow template.")
        comment_issue(
            issue_number,
            render_template(
                USER_TEMPLATES_DIR or DEFAULT_TEMPLATES_DIR, "invalid_template"
            ),
        )
        close_issue(issue_number)
        return

    # Check for duplicate issues based on title similarity
    duplicates = check_duplicate(issue, threshold=DUPLICATE_THRESHOLD)
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

    # Assign the issue to available contributors
    assignees = check_assignees(issue_number, k=2)
    if assignees:
        add_assignees(issue_number, assignees)
        print(f"INFO: Assigned issue to: {', '.join(assignees)}")
    else:
        print("INFO: No available contributors to assign the issue.")

    # Comment on the issue indicating successful processing
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
