# Milestone 0 test fixtures

该目录保存 AI2Doc 核心转换技术验证的输入与生成结果。

## Markdown 输入

- `basic.md`：标题、正文、列表、粗体和表格
- `math.md`：行内公式、块级二次方程和散度公式
- `chinese.md`：中文标题、段落、列表和表格

## Pandoc 默认样式输出

- `basic.docx`
- `math.docx`
- `chinese.docx`

## reference DOCX 输出

- `basic-academic.docx`
- `basic-report.docx`
- `basic-notes.docx`

以上文件由 Pandoc 3.9.0.2 生成。Microsoft Word 16.0 已成功打开全部六份输出；详细结构与视觉检查结果见 [`../milestone-0-report.md`](../milestone-0-report.md)。

视觉 QA 的 PDF/PNG 中间产物保存在被 Git 忽略的 `.qa/`，不作为交付物。
