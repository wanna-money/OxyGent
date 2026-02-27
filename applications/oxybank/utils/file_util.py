"""
File recursive processing utility

Provides recursive traversal of files and directories, MD5 calculation, file type detection, etc.
Supports the document ingestion process of the RAG system.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Set

from utils.hash_util import str_to_md5

# Supported file types set
SUPPORTED_FILE_TYPES = {
    "txt",
    "md",
    "markdown",
    "rst",
    "csv",
    "xlsx",
    "xls",
    "pdf",
    "docx",
    "doc",
}


def calculate_file_md5(file_path: str) -> str:
    """
    Calculate MD5 hash value of a file

    Args:
        file_path: Absolute path of the file

    Returns:
        str: MD5 hash value of the file (32-character hexadecimal string)

    Raises:
        FileNotFoundError: File does not exist
        PermissionError: No read permission
    """
    md5_hash = hashlib.md5()

    try:
        with open(file_path, "rb") as f:
            # Read file in chunks to avoid excessive memory usage for large files
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError(f"File does not exist: {file_path}")
    except PermissionError:
        raise PermissionError(f"No read permission: {file_path}")


def extract_file_type(file_path: str) -> str:
    """
    Extract file type (extension)

    Args:
        file_path: File path

    Returns:
        str: File extension (lowercase, without dot)
    """
    # Use pathlib to get suffix, remove dot and convert to lowercase
    suffix = Path(file_path).suffix.lstrip(".").lower()
    return suffix


def is_supported_file(
    file_path: str, supported_types: Optional[Set[str]] = None
) -> bool:
    """
    Check if file type is supported

    Args:
        file_path: File path
        supported_types: Set of supported file types, defaults to SUPPORTED_FILE_TYPES

    Returns:
        bool: Whether file type is supported
    """
    if supported_types is None:
        supported_types = SUPPORTED_FILE_TYPES

    file_type = extract_file_type(file_path)
    return file_type in supported_types
