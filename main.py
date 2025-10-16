"""Demo script."""

from src.epic_manager import JiraEpic
from src.schema import Story


def main() -> None:
    """Run the main function."""
    my_story = Story.from_json_file("example/mystory1.json")
    epic = JiraEpic()
    epic.create_stories([my_story])


if __name__ == "__main__":
    main()
