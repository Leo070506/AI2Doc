# AI2Doc Milestone 0 Report

## 0. Executive Summary

**结论：有条件通过（GO）。**

`Markdown + Pandoc + reference DOCX` 足以作为 AI2Doc MVP 的核心技术路线。基础结构、中文和测试范围内的 LaTeX 数学公式均能生成可由 Microsoft Word 打开的 DOCX；公式被转换为 Word 原生 OMML，而不是图片。

“有条件”是因为 reference DOCX 主要控制样式系统和页面部件，不能单独保证所有表格列宽、复杂 Markdown 方言和任意 LaTeX 宏都达到专业效果。建议在 Pandoc 前后增加窄而可测试的规范化/后处理层，不替换 Pandoc，也不在 MVP 引入复杂排版引擎。

## 1. Environment

验证日期：2026-08-14（Asia/Shanghai）

| Item | Result |
| --- | --- |
| OS | Microsoft Windows x64，版本 25H2，Build 26200.8875；注册表产品字符串为 `Windows 10 Home China` |
| Python | 3.12.13（Codex bundled workspace runtime） |
| Pandoc 初始状态 | 未安装，PATH 与 bundled runtime 中均未发现 `pandoc` |
| Pandoc 验证版本 | 3.9.0.2，Features `+server +lua`，Lua 5.4 |
| Pandoc 来源 | [官方 GitHub Release](https://github.com/jgm/pandoc/releases/tag/3.9.0.2) 的 Windows x86_64 ZIP |
| Pandoc ZIP SHA-256 | `c97542f2800f446e788d9f74237856d995421ad1bb3cc8324286840c5f272d3a`，与官方发布值一致 |
| Microsoft Word | 16.0，已用于真实打开与 PDF 导出验证 |
| LibreOffice | 未安装或不在 PATH |

Pandoc 便携副本只放在被 Git 忽略的 `.tools/` 下，没有修改系统 PATH。Phase 1 的后端镜像必须显式安装并固定 Pandoc 版本，不能依赖开发机状态。

### 验证方式

1. 使用 Pandoc CLI 生成 DOCX。
2. 将 DOCX 作为 ZIP/Open XML 包解析，校验 XML、段落样式、列表、表格和公式节点。
3. 使用 Microsoft Word 16.0 后台打开每份文件并导出 PDF，直接验证 Word 可读性。
4. 将每页 PDF 栅格化为 1224 × 1584 PNG 并逐页检查。

文档技能的标准 `render_docx.py` 已尝试运行，但因当前环境缺少 LibreOffice/`soffice` 无法完成；因此视觉验证采用 Word 自身导出路径。所有六份生成文档都被 Word 成功打开并导出。

## 2. Markdown Conversion Test

输入：[`tests/basic.md`](tests/basic.md)

输出：[`tests/basic.docx`](tests/basic.docx)

结果：**成功。**

| Check | Result |
| --- | --- |
| DOCX 生成 | 成功，10,966 bytes |
| Word 打开 | 成功，Word 16.0，1 页 |
| 标题层级 | H1 与 H2 均正确映射并显示 |
| 列表 | 4 个真实编号属性段落，项目符号显示正确 |
| 粗体 | `**Bold text**` 生成真实粗体 run |
| 表格 | 3 行 × 2 列，文本完整，表头与行结构正确 |
| 视觉缺陷 | 未发现裁切、重叠或缺字 |

说明：原任务样例中的 `Bold text` 没有 Markdown 粗体标记。测试夹具使用 `**Bold text**`，以实际验证粗体转换，而不是只列出功能名称。

观察：Pandoc 默认 DOCX 的表格样式非常克制，结构正确但视觉接近基础表格。这进一步证明 AI2Doc 需要 reference DOCX，而不是直接交付 Pandoc 默认样式。

## 3. Formula Test

输入：[`tests/math.md`](tests/math.md)

输出：[`tests/math.docx`](tests/math.docx)

结果：**成功，且为 Word 原生公式。**

| Formula | Visual result | OOXML evidence | Decision |
| --- | --- | --- | --- |
| 行内 `$E=mc^2$` | 正常显示，上标正确 | `m:oMath` | 通过 |
| 块级二次方程 | 分数、根号、正负号和指数正确 | `m:oMathPara` + `m:oMath` | 通过 |
| 散度公式 | `∇`、点乘、希腊字母与下标正确 | `m:oMathPara` + `m:oMath` | 通过 |

结构统计：

- `m:oMath`：3 个
- `m:oMathPara`：2 个
- `w:drawing`：0 个
- `word/media/` 嵌入文件：0 个

因此公式不是截图、SVG 或栅格图片，而是 Word 可编辑的 Office Math Markup Language（OMML）。Word 16.0 页面渲染未发现乱码、丢失或格式错误。

### 仍需注意的公式边界

本次只证明常用 TeX 数学语法可行，不代表完整 LaTeX 兼容。自定义宏、第三方宏包、复杂对齐环境、化学式和少见符号应在 Phase 1 建立扩展兼容矩阵。推荐方案：

1. MVP 明确支持 Pandoc TeX math 子集。
2. 在输入规范化层检测明显不支持的环境并返回可操作错误。
3. 不把公式转图片作为默认降级，因为会失去可编辑性与可访问性。

## 4. Chinese Document Test

输入：[`tests/chinese.md`](tests/chinese.md)

输出：[`tests/chinese.docx`](tests/chinese.docx)

结果：**成功。**

| Check | Result |
| --- | --- |
| Word 打开 | 成功，Word 16.0，1 页 |
| 中文字符 | 标题、正文、列表和表格均无乱码或缺字 |
| 标题层级 | 一个 H1、两个 H2，视觉层级清楚 |
| 列表 | 3 项，缩进和换行正常 |
| 表格 | 3 行 × 2 列，中英文混排正常 |
| 段落间距 | 自然，无重叠或异常大间隙 |

字体观察：Pandoc 默认 reference DOCX 的 `Normal` 样式未写入明确的 `w:rFonts`，由 Word 主题和本机字体回退决定。本机 Word 显示正常，但跨服务器/跨客户端的一致性存在风险。三个 AI2Doc 模板已显式设置东亚字体：academic 使用宋体；report 与 notes 使用微软雅黑。正式 Docker/生产方案仍需确定可合法分发或可靠存在的跨平台中文字体策略。

## 5. Template Test

模板：

- [`../templates/academic/template.docx`](../templates/academic/template.docx)
- [`../templates/report/template.docx`](../templates/report/template.docx)
- [`../templates/notes/template.docx`](../templates/notes/template.docx)

验证命令采用 Pandoc `--reference-doc=<template.docx>`，使用同一份 `basic.md` 生成：

- [`tests/basic-academic.docx`](tests/basic-academic.docx)
- [`tests/basic-report.docx`](tests/basic-report.docx)
- [`tests/basic-notes.docx`](tests/basic-notes.docx)

结果：**reference DOCX 可行。**

| Template | Style result | Header/footer | Word/visual result |
| --- | --- | --- | --- |
| academic | Times New Roman、中文宋体、居中学术标题、较宽正文节奏 | 研究标识 + 原生页码字段 | 成功，1 页，无视觉缺陷 |
| report | Calibri、深色商务标题、紧凑层级、浅灰表头 | Business Brief 标识 + 原生页码字段 | 成功，1 页，无视觉缺陷 |
| notes | Calibri、青绿色标题、较舒展列表、浅蓝灰表头 | Learning Notes 标识 + 原生页码字段 | 成功，1 页，无视觉缺陷 |

三个输出均保留真实标题样式、列表、表格、页眉、页脚和页码字段。模板确实能让相同 Markdown 产生可辨识的不同文档风格。

三份 `template.docx` 本身也均由 Word 16.0 成功打开并渲染为单页。Pandoc 默认 reference DOCX 自带的样式示例正文已被移除，因此模板文件只保留样式系统和页面部件，不携带会混入用户文档的占位正文。

### reference DOCX 的边界

- 擅长：页面尺寸、页边距、字体、标题梯度、段落节奏、颜色、页眉页脚和表格样式。
- 不足：Pandoc 生成的表格会携带自身网格/列宽信息，reference DOCX 不能针对每张表的内容自动优化列宽。本次短表结构正确且清晰，但宽度偏紧凑。
- 建议：保留 reference DOCX 作为主要模板机制；在生成后增加受控 OOXML/DOCX 后处理，仅处理列宽、单元格边距、文件名和少量 Pandoc 无法表达的专业排版规则。

## 6. Technical Decision

```diff
+ Markdown
+ Pandoc 3.9.0.2（服务器端固定版本）
+ DOCX reference template
+ 小型、可测试的输入规范化与 DOCX 后处理层
```

### 决策

继续采用该路线作为 AI2Doc MVP 核心。理由：

1. 基础 Markdown 结构已稳定生成有效 DOCX。
2. 常用数学公式直接转换为 Word 原生 OMML，满足核心差异化需求。
3. 中文内容在 Word 中显示正常，字体一致性问题可由模板策略控制。
4. reference DOCX 能用同一转换引擎产生不同用途的视觉系统。
5. Pandoc 只需部署在服务器，符合用户零安装目标。
6. 局限集中在可控的输入子集和局部排版后处理，无需自研完整 DOCX 引擎。

### MVP 执行模型建议

Phase 1 采用单实例、受限并发、有超时的 Pandoc 子进程即可；不引入数据库、Redis 或复杂任务队列。API 可保留任务资源模型，但执行层先使用进程内调度，并明确它不具备跨实例恢复能力。

## 7. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| AI 产品输出的 Markdown 方言不同 | 表格、代码块或嵌套列表结果不一致 | 定义支持子集，建立跨来源夹具并先规范化 |
| LaTeX 不是完整兼容 | 复杂宏或环境转换失败 | 建立公式矩阵、检测不支持语法、保留原文与明确错误 |
| CJK 字体跨环境不一致 | 换行、分页和字形发生变化 | 显式东亚字体、固定部署字体、许可审查与视觉回归 |
| Pandoc 升级导致输出变化 | 模板或 OOXML 断言回归 | 固定版本；升级走兼容矩阵与 Golden fixtures |
| reference DOCX 无法优化所有布局 | 宽表格、代码块和分页不够专业 | 小型后处理层；针对结构而非内容硬编码 |
| Word 与 LibreOffice 渲染差异 | 用户看到不同分页或公式表现 | CI 同时做 OOXML 结构检查和至少一个真实渲染器检查 |
| 不受信任内容触发资源访问或耗尽 | 安全与稳定性风险 | 禁止远程资源/任意 filter，设置大小、时间和并发限制 |
| 临时文件残留 | 隐私泄漏与磁盘增长 | 独立任务目录、下载后删除、TTL、启动扫描与指标 |
| 任务状态只在内存 | 多实例或重启时丢失 | MVP 明确单实例；达到需求后替换存储接口 |

文件处理细节见 [`file-lifecycle.md`](file-lifecycle.md)。

## 8. File Lifecycle Decision

MVP 推荐流程：

```text
validate input
→ create isolated temporary task directory
→ run bounded Pandoc conversion
→ validate and atomically publish output.docx
→ delete input/intermediates
→ stream download
→ delete output after stream closes
→ TTL/startup sweep as fallback
```

默认建议 TTL 为 60 分钟。正文、公式、服务器路径和完整 Pandoc 参数不得进入日志。此阶段只完成设计，没有实现文件生命周期代码。

## 9. Next-stage Recommendation

Milestone 0 已达到技术可行性目标。下一步可以进入 **Milestone 1：工程脚手架与质量门禁**，但建议继续保持小步交付：

1. 固定 Python 3.12、Pandoc 3.9.0.2 与候选 Node.js 版本。
2. 创建最小 FastAPI 健康检查和 Pandoc readiness 检查。
3. 创建 Vue 3 + TypeScript + Vite + Tailwind 空白工程。
4. 创建 Dockerfile/Compose，使 Pandoc 只存在于后端镜像。
5. 把本轮 Markdown、DOCX 结构断言和模板 smoke test 纳入 CI。

不要在该阶段同时实现用户系统、数据库、AI API、复杂队列或浏览器插件。

## 10. Validation Artifacts

- Markdown 夹具与六份 DOCX：[`tests/`](tests/)
- 三份 reference DOCX：[`../templates/`](../templates/)
- 文件生命周期设计：[`file-lifecycle.md`](file-lifecycle.md)

PDF 和 PNG 只用于本地视觉 QA，存放在被 Git 忽略的 `.qa/`，不属于项目交付物。
