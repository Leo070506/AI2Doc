# Changelog

AI2Doc 的重要变更记录在此文件中。版本格式遵循 [Semantic Versioning](https://semver.org/)，内容结构参考 [Keep a Changelog](https://keepachangelog.com/)。

## 0.1.0 - Unreleased

### Added

- 粘贴 AI 回答或上传 UTF-8 Markdown 文件。
- 使用 Pandoc 将 Markdown 转换为可编辑 DOCX。
- 支持标题、段落、列表、表格和常用 Markdown 结构。
- 将常用 LaTeX 行内与块级公式转换为 Word 原生 OMML。
- 支持中文内容和 Academic、Report、Notes 三种 reference DOCX 模板。
- 提供 Vue 3、TypeScript、Vite 与 Tailwind CSS Web 界面。
- 提供 FastAPI 转换、一次性下载和健康检查接口。
- 提供下载后删除、失败清理与过期清理的临时文件生命周期。
- 提供 Docker Compose、Nginx 同源代理和后端 Pandoc 运行环境定义。
- 提供后端测试、前端类型检查、生产构建和 GitHub Actions 工作流。
- 提供安全策略、贡献指南、Issue/PR 模板、公开示例与项目截图。

### Security

- 限制输入、输出和请求体大小。
- 使用模板白名单、不可预测下载令牌和隔离临时目录。
- 以参数数组且不经过 shell 的方式调用 Pandoc，并限制执行时间。
- 默认不永久保存用户内容。

### Known limitations

- Docker 后端镜像当前固定为 `linux/amd64`。
- MVP 不包含登录、限流、数据库、云存储、AI API 或多进程任务状态共享。
