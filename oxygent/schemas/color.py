from enum import Enum, auto

"""
Color enum module

The Color enum is used to represent the color on terminal.
"""


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
