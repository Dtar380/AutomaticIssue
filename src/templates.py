#################################################
#  MODULE DESCRIPTION
#################################################
"""
This module provides functionality to render Jinja2 templates for GitHub comments.
"""

#################################################
#  Importing MODULES
#################################################
from __future__ import annotations

# STANDARD MODULES
from pathlib import Path

# EXTERNAL MODULES
from jinja2 import Environment, FileSystemLoader, select_autoescape


#################################################
#  CODE
#################################################
def render_template(
    template_path: Path, template_name: str, **variables
) -> str:
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

    # Check if the template path exists and is a directory
    if not template_path.exists() or not template_path.is_dir():
        raise FileNotFoundError("ERROR: Templates directory not found.")

    # Set up the Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_path)),
        autoescape=select_autoescape(["md"]),
    )

    print(template_path)

    # Load and render the template
    try:
        template = env.get_template(f"{template_name}.j2")
        return template.render(**variables)
    except Exception as e:
        print(f"ERROR: An error occurred while rendering the template: {e}")
        return "Error rendering template. Please contact maintainers."
