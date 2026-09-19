import tempfile
import unittest
from pathlib import Path

import pandas as pd

from attendance_tool.core import apply_attendance, extract_present_names
from attendance_tool.cli import main


class ExtractPresentNamesTests(unittest.TestCase):
    def test_extracts_names_and_ignores_layout_labels(self) -> None:
        attendance = pd.DataFrame(
            [
                ["示例甲", "  示例乙  ", "过道", "第一排"],
                [None, "窗户", "门", "第二排"],
            ]
        )

        names = extract_present_names(attendance)

        self.assertEqual(names, {"示例甲", "示例乙"})

    def test_can_keep_last_column(self) -> None:
        attendance = pd.DataFrame([["示例甲", "示例乙"]])

        names = extract_present_names(attendance, drop_last_column=False)

        self.assertEqual(names, {"示例甲", "示例乙"})


class ApplyAttendanceTests(unittest.TestCase):
    def test_adds_one_column_per_date_without_mutating_input(self) -> None:
        roster = pd.DataFrame(
            {
                "序号": [1, 2, 3],
                "姓名": ["示例甲", "示例乙", "示例丙"],
            }
        )

        updated = apply_attendance(
            roster,
            {
                "2024-10-08": {"示例甲", "示例丙"},
                "2024-10-10": {"示例乙"},
            },
        )

        self.assertNotIn("考勤_2024-10-08", roster.columns)
        self.assertEqual(updated["考勤_2024-10-08"].tolist(), ["√", "×", "√"])
        self.assertEqual(updated["考勤_2024-10-10"].tolist(), ["×", "√", "×"])

    def test_rejects_missing_name_column(self) -> None:
        roster = pd.DataFrame({"学号": [1]})

        with self.assertRaisesRegex(ValueError, "找不到姓名列"):
            apply_attendance(roster, {"2024-10-08": set()})


class CommandLineIntegrationTests(unittest.TestCase):
    def test_reads_workbooks_and_writes_updated_roster(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            roster_path = root / "roster.xlsx"
            attendance_path = root / "attendance.xlsx"
            output_path = root / "result.xlsx"

            pd.DataFrame({"姓名": ["示例甲", "示例乙"]}).to_excel(
                roster_path, index=False
            )
            pd.DataFrame(
                [
                    ["标题", None, None],
                    [None, None, None],
                    [None, None, None],
                    ["示例甲", "过道", "第一排"],
                ]
            ).to_excel(attendance_path, index=False, header=False)

            exit_code = main(
                [
                    "--roster",
                    str(roster_path),
                    "--attendance",
                    f"2024-10-08={attendance_path}",
                    "--output",
                    str(output_path),
                ]
            )

            result = pd.read_excel(output_path)
            self.assertEqual(exit_code, 0)
            self.assertEqual(result["考勤_2024-10-08"].tolist(), ["√", "×"])


if __name__ == "__main__":
    unittest.main()
