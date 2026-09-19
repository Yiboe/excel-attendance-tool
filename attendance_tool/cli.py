from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path

from .core import DEFAULT_EXCLUDED_LABELS, apply_attendance, load_attendance, load_roster


def attendance_spec(value: str) -> tuple[str, Path]:
    date_text, separator, path_text = value.partition("=")
    if not separator or not date_text or not path_text:
        raise argparse.ArgumentTypeError("格式应为 YYYY-MM-DD=考勤文件路径")
    try:
        date.fromisoformat(date_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"无效日期：{date_text}") from error
    return date_text, Path(path_text).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="把座位表式 Excel 考勤记录合并到学生花名册。"
    )
    parser.add_argument("--roster", required=True, type=Path, help="学生花名册 Excel 文件")
    parser.add_argument(
        "--attendance",
        required=True,
        action="append",
        type=attendance_spec,
        metavar="YYYY-MM-DD=FILE",
        help="考勤日期和文件；可重复提供",
    )
    parser.add_argument("--output", type=Path, help="输出 Excel 文件")
    parser.add_argument("--name-column", default="姓名", help="花名册的姓名列名")
    parser.add_argument(
        "--skip-rows",
        type=int,
        default=3,
        help="考勤表顶部跳过的行数（默认：3）",
    )
    parser.add_argument(
        "--exclude-label",
        action="append",
        default=[],
        help="额外忽略的座位表标签；可重复提供",
    )
    parser.add_argument(
        "--keep-last-column",
        action="store_true",
        help="把考勤表最后一列也当作姓名区域",
    )
    parser.add_argument("--force", action="store_true", help="允许覆盖已有输出文件")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.skip_rows < 0:
        parser.error("--skip-rows 不能小于 0")
    if not args.roster.is_file():
        parser.error(f"花名册不存在：{args.roster}")

    output = args.output or args.roster.with_name(f"{args.roster.stem}_updated.xlsx")
    if output.exists() and not args.force:
        parser.error(f"输出文件已存在：{output}；如需覆盖请添加 --force")

    excluded_labels = set(DEFAULT_EXCLUDED_LABELS)
    excluded_labels.update(args.exclude_label)
    names_by_date: defaultdict[str, set[str]] = defaultdict(set)

    for attendance_date, attendance_path in args.attendance:
        if not attendance_path.is_file():
            parser.error(f"考勤文件不存在：{attendance_path}")
        names_by_date[attendance_date].update(
            load_attendance(
                attendance_path,
                skip_rows=args.skip_rows,
                excluded_labels=excluded_labels,
                drop_last_column=not args.keep_last_column,
            )
        )

    try:
        roster = load_roster(args.roster)
        updated = apply_attendance(
            roster,
            names_by_date,
            name_column=args.name_column,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))

    output.parent.mkdir(parents=True, exist_ok=True)
    updated.to_excel(output, index=False)
    print(f"已保存：{output}")
    print(f"处理日期：{len(names_by_date)}；花名册人数：{len(updated)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
