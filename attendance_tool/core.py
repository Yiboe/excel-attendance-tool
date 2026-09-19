from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

import pandas as pd


DEFAULT_EXCLUDED_LABELS = frozenset({"门", "过道", "窗户"})


def normalize_cell(value: object) -> str | None:
    """Return a trimmed cell value, or None for an empty cell."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def load_roster(path: str | Path) -> pd.DataFrame:
    """Load an Excel roster without changing its columns."""
    return pd.read_excel(Path(path))


def extract_present_names(
    attendance: pd.DataFrame,
    *,
    excluded_labels: Iterable[str] = DEFAULT_EXCLUDED_LABELS,
    drop_last_column: bool = True,
) -> set[str]:
    """Extract unique attendee names from a seat-layout DataFrame."""
    excluded = {label.strip() for label in excluded_labels if label.strip()}
    seat_cells = attendance
    if drop_last_column and attendance.shape[1] > 1:
        seat_cells = attendance.iloc[:, :-1]

    names: set[str] = set()
    for value in seat_cells.to_numpy().ravel():
        name = normalize_cell(value)
        if name is not None and name not in excluded:
            names.add(name)
    return names


def load_attendance(
    path: str | Path,
    *,
    skip_rows: int = 3,
    excluded_labels: Iterable[str] = DEFAULT_EXCLUDED_LABELS,
    drop_last_column: bool = True,
) -> set[str]:
    """Load an Excel seat layout and return the names marked present."""
    attendance = pd.read_excel(Path(path), header=None, skiprows=skip_rows)
    return extract_present_names(
        attendance,
        excluded_labels=excluded_labels,
        drop_last_column=drop_last_column,
    )


def apply_attendance(
    roster: pd.DataFrame,
    names_by_date: Mapping[str, Iterable[str]],
    *,
    name_column: str = "姓名",
    present_mark: str = "√",
    absent_mark: str = "×",
) -> pd.DataFrame:
    """Return a roster copy with one attendance column per date."""
    if name_column not in roster.columns:
        available = ", ".join(map(str, roster.columns))
        raise ValueError(
            f"花名册中找不到姓名列 {name_column!r}。现有列：{available or '（无）'}"
        )

    result = roster.copy()
    roster_names = result[name_column].map(normalize_cell)

    for date, names in names_by_date.items():
        present_names = {
            normalized
            for value in names
            if (normalized := normalize_cell(value)) is not None
        }
        column_name = f"考勤_{date}"
        result[column_name] = absent_mark
        result.loc[roster_names.isin(present_names), column_name] = present_mark

    return result
