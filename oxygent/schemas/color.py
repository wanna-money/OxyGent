"""ANSI terminal color definitions for styled log output."""

from enum import Enum, auto


class Color(Enum):
    """ANSI terminal color codes for styled log output."""

    DEFAULT = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    YELLOW = auto()
    BLUE = auto()
    MAGENTA = auto()
    CYAN = auto()
    WHITE = auto()
