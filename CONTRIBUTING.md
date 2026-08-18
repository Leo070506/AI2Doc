# Contributing to AI2Doc

感谢你考虑参与 AI2Doc。项目目前处于首个公开版本准备期，欢迎从问题复现、文档改进、测试补充和小范围修复开始贡献。

## 提交 Issue

提交前请先搜索现有 Issue，避免重复。一个高质量 Issue 应包含：

- 清晰、可检索的标题
- 使用场景以及期望结果
- 实际结果和最小复现步骤（适用于缺陷）
- 操作系统、浏览器、Python/Node.js/Pandoc 版本（如相关）
- 可公开的示例输入与输出；请删除私人、敏感或受版权保护的内容
- 日志或截图；日志中不要包含原始文档内容、令牌或密钥

安全漏洞请不要提交公开 Issue。请按照 [`SECURITY.md`](SECURITY.md) 使用 GitHub Private Vulnerability Reporting。

## 开发准备

项目技术栈：

- Frontend：Vue 3、TypeScript、Vite、Tailwind CSS
- Backend：Python、FastAPI、Pandoc
- Deployment：Docker Compose

最短启动方式见 [`README.md`](README.md)。本地开发的环境变量、测试与 Pandoc 配置见 [`docs/mvp-development.md`](docs/mvp-development.md)。架构或 API 变更必须先更新 `docs/` 中的设计文档。

## 分支规范

不要直接向 `main` 提交。请从最新的 `main` 创建单一目的的短生命周期分支：

- `feat/<topic>`：新功能
- `fix/<topic>`：缺陷修复
- `docs/<topic>`：文档更新
- `refactor/<topic>`：不改变外部行为的重构
- `test/<topic>`：测试变更
- `chore/<topic>`：工程维护

名称使用小写英文和连字符，例如 `feat/docx-download`。

## 代码规范

通用要求：

- 优先可读性、明确边界和小模块，避免“万能工具类”与超大文件
- 新行为必须有测试；缺陷修复应包含能复现问题的回归测试
- 公共接口、环境变量和用户可见行为变更必须同步更新文档
- 不提交密钥、个人数据、生成的用户文档或大型二进制文件
- 核心流程不直接依赖商业 AI API

Frontend 约定：

- TypeScript 开启严格模式
- Vue 组件职责单一；网络请求集中在 `src/api/`
- 共享逻辑使用组合式函数或 `utils`，页面组件不直接拼接 API URL
- 提交前运行 `npm run typecheck` 和 `npm run build`

Backend 约定：

- 路由层只负责协议转换、校验和状态码，业务编排放在 `services/`
- Pandoc 调用封装在独立适配器中，禁止把用户输入拼接为 shell 命令
- 所有文件操作必须限定在每次任务独立的临时目录内
- Python 公共函数和数据模型使用类型标注
- 工具函数必须无隐藏的请求级状态
- 提交前运行 `python -m pytest`

## Commit 规范

推荐使用 Conventional Commits：

```text
feat: add document conversion endpoint
fix: reject unsupported template identifier
docs: clarify temporary file lifecycle
```

一次提交应表达一个完整意图。提交信息说明“为什么改变”，避免只描述文件名。

## 提交 Pull Request

1. 先为较大功能或架构变化创建 Issue，确认范围。
2. 保持 PR 小而聚焦；不要夹带无关格式化或重构。
3. 填写问题背景、解决方案、测试方式和潜在风险。
4. 关联对应 Issue，例如 `Closes #123`。
5. 确保文档、测试、lint、类型检查与构建全部通过。
6. 涉及 UI 时提供截图；涉及 DOCX 输出时提供不含敏感数据的验证说明。
7. 根据评审意见追加提交；合并前可由维护者整理提交历史。

提交 PR 即表示你有权贡献相关内容，并同意其按本项目 MIT License 发布。

## 设计变更

出现以下情况时，应先更新或新增设计文档，再写实现：

- 改变公共 API 或文件生命周期
- 引入新的外部服务或核心依赖
- 改变模块边界、部署拓扑或安全模型
- 引入向后不兼容行为

设计讨论至少说明问题、约束、备选方案、选择理由和迁移影响。
