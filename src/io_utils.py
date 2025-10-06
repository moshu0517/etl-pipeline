"""
Simple IO helpers to make file operations safer and cleaner.
I don’t want ETL code to crash just because a folder doesn’t exist.
This keeps extract/transform/load steps focused on logic, not filesystem issues.

How it fits the pipeline
- Used across all stages whenever we read/write data files.
- Prevents repetitive boilerplate for checking directories.

Rule of thumb: never assume a folder exists — just call ensure_parent_dir().
"""


from pathlib import Path

def ensure_parent_dir(path: Path) -> None:
    """
    Make sure the parent directory of a given path exists.
    This prevents 'No such file or directory' errors when saving files.
    """
    path.parent.mkdir(parents=True, exist_ok=True)