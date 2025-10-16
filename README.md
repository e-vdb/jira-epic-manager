# Jira Epic Manager

This tool allows you to create stories and sub-tasks in a Jira epic.

## Getting started


Create a .env file with the following

```
JIRA_EMAIL = myemail
JIRA_TOKEN = mytoken
JIRA_ID = myjiraid
JIRA_HOST = myhost.atlassian.net
JIRA_PROJECT = MYPROJECT
JIRA_EPIC_KEY = MYEPIC-1
```

Create a story json file following the template in the example folder.

```json
{
    "summary": "My Story 1",
    "description": "My Story 1 Description",
    "tasks": [
        {
            "summary": "My Task 1",
            "description": "My Task 1 Description"
        },
        {
            "summary": "My Task 2",
            "description": "My Task 2 Description"
        },
        {
            "summary": "My Task 3",
            "description": "My Task 3 Description"
        }
    ]
}
```

Run the demo script

```python
"""Demo script."""

from src.schema import Story
from src.epic_manager import JiraEpic

def main():
    my_story = Story.from_json_file("example/mystory1.json") # change this to your story json file
    epic = JiraEpic()
    results = epic.create_stories([my_story])
    print(results)


if __name__ == "__main__":
    main()
```
