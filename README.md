# Automatic Issue GH Action
## Automate your GH issues with GH Actions

<div align="center">
    <img alt="license" title="License" src="https://custom-icon-badges.demolab.com/github/license/Dtar380/AutomaticIssue?style=for-the-badge&logo=law&logoColor=white&labelColor=1155BA&color=236AD3" height=30>
    <img alt="stars" title="stars" src="https://custom-icon-badges.demolab.com/github/stars/Dtar380/AutomaticIssue?style=for-the-badge&logo=star&logoColor=white&label=STARS&labelColor=9133D4&color=A444E0" height=30>
    <img alt="release" title="release" src="https://img.shields.io/github/v/release/dtar380/AutomaticIssue?style=for-the-badge&logo=download&logoColor=white&label=Release&labelColor=488207&color=55960C" height=30>
    <img alt="Visitors" title="Visitors" src="https://viewcounterpython.onrender.com/Dtar380/AutomaticIssue">
    <img alt="open issues" title="open issues" src="https://custom-icon-badges.demolab.com/github/issues/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=issue-opened&logoColor=white&label=open%20issues&labelColor=CE4630&color=E05D44" height=30>
</div>

**AutomaticIssue** aims to automate the initial process of reviewing if an issue is valid and assigning someone to attend the issue.

## :blue_heart: **Main Features**
- **Checks if issue follows template and has the desired data**
- **Checks if the issue is repeated or a duplicate**
- **Auto assigns any online collaborators**

## :: **How to use**

### Inputs
| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `token` | GitHub Token with repo permissions | :white_check_mark: | N/A |
| `repo` | GitHub repository in format `owner/repo` | :white_check_mark: | N/A |
| `duplicate_threshold` | Similarity threshold to detect duplicates (0-100) | :x: | "80" |
| `comment_templates_path` | Path to comment templates (Jinja2) | :x: | Default templates |

### Example
```yaml
name: Automate Issues

on:
    issues:
        types: [opened]

jobs:
    automate:
        runs-on: ubuntu-latest
        steps:
            - name: Check out repository
              uses: actions/checkout@v5

            - name: Issue Automation
              uses: dtar380/AutomaticIssue@v1.0.0
              with:
                token: ${{ secrets.GITHUB_TOKEN }}
                repo: ${{ github.repository }}
```

## :open_file_folder: **Kown Issues**
There is no known issues on the project, you can submit yours to [issues](https://github.com/Dtar380/MinecraftDockerCLI/issues/new/choose).

## :scroll: **License**
This project is distributed under the MIT license.
See the [LICENSE](LICENSE).

## :money_with_wings: **Sponsorship**
You can support me and the project with a donation to my Ko-Fi.
