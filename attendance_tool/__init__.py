"""Excel attendance roster utilities."""

from .core import apply_attendance, extract_present_names, load_attendance, load_roster

__all__ = [
    "apply_attendance",
    "extract_present_names",
    "load_attendance",
    "load_roster",
]

__version__ = "1.0.0"
