# Excel 考勤汇总工具

一个用于课程作业和日常教学的小型命令行工具：从座位表式的 Excel 考勤文件中提取到课名单，并在学生花名册中按日期生成考勤列。

## 功能

- 一次合并一个或多个日期的考勤表
- 自动生成 `考勤_YYYY-MM-DD` 列
- 到课标记为 `√`，缺勤标记为 `×`
- 自动忽略 `门`、`过道`、`窗户` 等座位表标签
- 支持自定义姓名列、跳过行数和额外排除标签
- 默认拒绝覆盖已有输出文件

## 安装

需要 Python 3.9 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## 使用

```powershell
attendance-tool `
  --roster "data\学生花名册.xlsx" `
  --attendance "2024-10-08=data\10月8日考勤.xlsx" `
  --attendance "2024-10-10=data\10月10日考勤.xlsx" `
  --output "output\考勤汇总.xlsx"
```

也可以不安装，直接运行：

```powershell
python -m attendance_tool --roster "data\学生花名册.xlsx" --attendance "2024-10-08=data\10月8日考勤.xlsx"
```

如果省略 `--output`，结果会保存为花名册同目录下的 `原文件名_updated.xlsx`。

### 常用选项

```text
--name-column 姓名       花名册中的姓名列名
--skip-rows 3           考勤表顶部需要跳过的行数
--exclude-label 讲台     追加需要忽略的座位表标签
--keep-last-column      不忽略考勤表的最后一列
--force                 允许覆盖已有输出文件
```

考勤表默认按原脚本的格式处理：跳过顶部 3 行，把最后一列视为时间或备注，其余非空单元格视为到课姓名。若你的表格结构不同，可通过上述选项调整。

## 数据格式

花名册第一行需要包含 `姓名` 列；列名可用 `--name-column` 修改。工具会保留花名册中的其他列。

考勤表可以采用座位表布局。示意如下，其中最后一列为备注列：

| 座位 1 | 座位 2 | 座位 3 | 备注 |
| --- | --- | --- | --- |
| 示例甲 | 示例乙 | 过道 | 第一排 |
| 示例丙 | 窗户 | 示例丁 | 第二排 |

示意姓名均为虚构内容，不对应真实学生。

仓库中的 [`考勤表.xlsx`](考勤表.xlsx) 是保留原表布局后生成的完全脱敏示例，可直接用于了解输入格式。文件内的姓名、标题、备注和文档作者信息均为虚构内容。

## 隐私说明

除完全脱敏的 `考勤表.xlsx` 示例外，本仓库不会提交真实花名册、考勤记录或生成结果。`.gitignore` 已默认排除其他 Excel、CSV、`data/` 和 `output/`。请在提交前继续检查暂存区，避免上传姓名、学号、手机号、邮箱、个人路径或其他敏感信息。

## 测试

```powershell
python -m unittest discover -s tests -v
```

## 许可证

[MIT](LICENSE)
