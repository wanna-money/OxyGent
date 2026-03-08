import os
import shutil
from typing import Optional, List

from pydantic import Field

from oxygent.oxy import FunctionHub

file_tools = FunctionHub(name="file_tools")


@file_tools.tool(
    description="Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories."
)
def write_file(
        path: str = Field(description="Full path to the file to write"),
        content: str = Field(description="The content to write to the file")
) -> str:
    """Write content to a file, creating it if it doesn't exist or overwriting if it does.

    Args:
        path: Full path to the file
        content: Text content to write

    Returns:
        Success or error message
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Successfully wrote to {path}"
    except PermissionError:
        return f"Error: Permission denied when trying to write to {path}"
    except Exception as e:
        return f"Error: Failed to write to {path}. Reason: {str(e)}"


@file_tools.tool(
    description="Read the content of a file. Returns the raw content without line numbers. For viewing with line numbers and range support, use view_text_file instead."
)
def read_file(path: str = Field(description="Path to the file to read")) -> str:
    """Read the entire content of a file without line numbers.

    Args:
        path: Path to the file

    Returns:
        File content or error message
    """
    if not os.path.exists(path):
        return f"Error: The file at {path} does not exist."

    if not os.path.isfile(path):
        return f"Error: The path {path} is not a file."

    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except PermissionError:
        return f"Error: Permission denied when trying to read {path}"
    except Exception as e:
        return f"Error: Failed to read {path}. Reason: {str(e)}"


@file_tools.tool(
    description="View the content of a text file with line numbers and optional range support. "
                "Returns file content with line numbers. Useful for viewing specific sections of large files. "
                "Supports negative indices to view from the end of the file (e.g., [-100, -1] for last 100 lines)."
)
def view_text_file(
        file_path: str = Field(description="The target file path. Supports ~ expansion for home directory."),
        ranges: Optional[List[int]] = Field(
            default=None,
            description="The range of lines to be viewed (e.g. [1, 100] for lines 1 to 100), inclusive. "
                        "If not provided, the entire file will be returned. "
                        "To view the last 100 lines, use [-100, -1]."
        )
) -> str:
    """View the file content in the specified range with line numbers.

    If `ranges` is not provided, the entire file will be returned.

    Args:
        file_path: The target file path. Supports ~ expansion for home directory.
        ranges: The range of lines to be viewed (e.g. [1, 100] for lines 1 to 100),
                inclusive. If not provided, the entire file will be returned.
                To view the last 100 lines, use [-100, -1].

    Returns:
        The file content with line numbers, or an error message.
    """
    file_path = os.path.expanduser(file_path)

    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."

    if not os.path.isfile(file_path):
        return f"Error: The path {file_path} is not a file."

    try:
        content = _read_file_with_range(file_path, ranges)
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: Failed to read file: {str(e)}"

    if ranges is None:
        return f"The content of {file_path}:\n```\n{content}\n```"
    else:
        return f"The content of {file_path} in lines {ranges[0]}-{ranges[1]}:\n```\n{content}\n```"


def _read_file_with_range(file_path: str, ranges: Optional[List[int]] = None) -> str:
    """Read file content with optional line range.

    Args:
        file_path: Path to the file.
        ranges: Optional list of [start, end] line numbers (1-indexed, inclusive).
                Negative indices count from the end (-1 is the last line).

    Returns:
        File content with line numbers.

    Raises:
        ValueError: If ranges are invalid.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)

    if ranges is None:
        # Return all lines with line numbers
        return "".join(f"{i + 1} | {line}" for i, line in enumerate(lines))

    if len(ranges) != 2:
        raise ValueError("ranges must be a list of two integers [start, end]")

    start, end = ranges

    # Handle negative indices
    if start < 0:
        start = total_lines + start + 1
    if end < 0:
        end = total_lines + end + 1

    # Validate range
    if start < 1:
        start = 1
    if end > total_lines:
        end = total_lines
    if start > end:
        raise ValueError(f"Invalid range: start ({start}) > end ({end})")

    # Convert to 0-indexed
    start_idx = start - 1
    end_idx = end

    # Return lines with line numbers
    return "".join(f"{i + 1} | {lines[i]}" for i in range(start_idx, end_idx))


@file_tools.tool(
    description="Delete a file or directory. Returns a success message if the item is deleted, or an error if the item does not exist. For directories, this will delete all contents recursively."
)
def delete_file(
        path: str = Field(description="Path to the file or directory to delete"),
) -> str:
    """Delete a file or directory recursively.

    Args:
        path: Path to the file or directory to delete

    Returns:
        Success or error message
    """
    if not os.path.exists(path):
        return f"Error: The file or directory at {path} does not exist."

    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"Successfully deleted the file at {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Successfully deleted the directory at {path} and all its contents"
    except PermissionError:
        return f"Error: Permission denied when trying to delete {path}"
    except Exception as e:
        return f"Error: Failed to delete {path}. Reason: {str(e)}"


@file_tools.tool(
    description="List the contents of a directory. Returns files and directories with their types. "
                "Useful for exploring directory structure and finding files."
)
def list_directory(
        path: str = Field(description="Path to the directory to list"),
        show_hidden: bool = Field(
            default=False,
            description="Whether to show hidden files (files starting with .)"
        )
) -> str:
    """List the contents of a directory.

    Args:
        path: Path to the directory
        show_hidden: Whether to show hidden files (default: False)

    Returns:
        Formatted list of files and directories, or error message
    """
    path = os.path.expanduser(path)

    if not os.path.exists(path):
        return f"Error: The directory {path} does not exist."

    if not os.path.isdir(path):
        return f"Error: The path {path} is not a directory."

    try:
        items = []
        for item in sorted(os.listdir(path)):
            # Skip hidden files unless requested
            if not show_hidden and item.startswith('.'):
                continue

            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                items.append(f"📄 {item}")
            elif os.path.isdir(item_path):
                items.append(f"📁 {item}/")
            else:
                items.append(f"🔗 {item}")

        if not items:
            return f"The directory {path} is empty."

        return f"Contents of {path}:\n" + "\n".join(items)
    except PermissionError:
        return f"Error: Permission denied when trying to list {path}"
    except Exception as e:
        return f"Error: Failed to list {path}. Reason: {str(e)}"
