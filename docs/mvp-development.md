# AI2Doc Milestone 1 — Web MVP Development

> 状态：已完成（2026-08-14）

## 1. 目标

本里程碑实现第一个可运行闭环：

```text
paste text / upload Markdown
→ choose academic, report, or notes
→ conservative Markdown cleanup
→ server-side Pandoc conversion
→ one-time DOCX download
→ temporary file deletion
```

明确不包含用户、数据库、登录、AI API、支付、浏览器插件、云存储和复杂任务队列。

## 2. 固定技术基线

### Backend

- Python 3.12
- FastAPI 0.139.2
- Uvicorn 0.51.0
- python-multipart 0.0.32
- Pandoc 3.9.0.2
- pytest 9.1.1

### Frontend

- Node.js 24（开发基线；Docker 使用固定 LTS 镜像）
- Vue 3.5.40
- TypeScript 6.0.3
- Vite 7.3.6
- Tailwind CSS 4.3.3

版本升级必须重新运行 Markdown、数学、中文、模板和前端构建检查。

## 3. 开发顺序

1. 更新 API、架构、生命周期和本文件。
2. 实现可注入配置、模板白名单和临时文件存储。
3. 实现 Markdown 保守清理和 Pandoc 适配器。
4. 实现转换、一次性下载和健康检查 API。
5. 先通过后端单元/集成测试，再接入 Vue 页面。
6. 完成 Docker 构建定义和同源反向代理。
7. 执行前端构建、API smoke test、DOCX 结构检查和 Word 视觉验证。

## 4. 本地启动

### 4.1 Backend

Pandoc 必须安装在开发机，或通过 `AI2DOC_PANDOC_PATH` 指向可执行文件。

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

本仓库 Milestone 0 使用的便携版可在 PowerShell 中这样配置：

```powershell
$env:AI2DOC_PANDOC_PATH = "..\.tools\pandoc-3.9.0.2\pandoc-3.9.0.2\pandoc.exe"
```

### 4.2 Frontend

```bash
cd frontend
npm install
npm run dev
```

打开 `http://localhost:5173`。Vite 把 `/api` 和 `/health` 代理到 `http://localhost:8000`。

## 5. Docker 启动

```bash
docker compose up --build
```

打开 `http://localhost:8080`。Docker 中 Pandoc 只安装在 backend 镜像；frontend 通过 Nginx 将 `/api` 与 `/health` 转发给 backend。

Milestone 1 后端镜像固定使用 Pandoc 官方 amd64 Debian 包，因此 Compose 将 backend 固定为 `linux/amd64`；ARM 开发机需要容器运行时提供架构模拟。原生 ARM 镜像属于后续发布工程。

## 6. 配置

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI2DOC_PANDOC_PATH` | `pandoc` | Pandoc 可执行文件或 PATH 名称 |
| `AI2DOC_STORAGE_ROOT` | `backend/app/storage/temp` | 临时任务目录 |
| `AI2DOC_TEMPLATES_ROOT` | repository `templates/` | reference DOCX 根目录 |
| `AI2DOC_MAX_INPUT_BYTES` | `1048576` | Markdown 最大字节数 |
| `AI2DOC_MAX_OUTPUT_BYTES` | `10485760` | DOCX 最大字节数 |
| `AI2DOC_CONVERSION_TIMEOUT_SECONDS` | `30` | 单次 Pandoc 超时 |
| `AI2DOC_FILE_TTL_SECONDS` | `3600` | 未下载输出存活时间 |
| `AI2DOC_CLEANUP_INTERVAL_SECONDS` | `60` | 过期清理周期 |
| `AI2DOC_CORS_ORIGINS` | `http://localhost:5173` | 本地开发跨域来源，逗号分隔 |

## 7. API 使用

### JSON 文本

```bash
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"content":"# Hello","template":"report"}'
```

### Markdown 文件

```bash
curl -X POST http://localhost:8000/api/convert \
  -F "template=academic" \
  -F "file=@notes.md;type=text/markdown"
```

响应中的 `file` 是一次性下载地址。

## 8. 测试

### Backend

```bash
cd backend
pytest
```

测试覆盖：

- Markdown 标题、列表、粗体和表格
- 行内/块级数学公式及原生 OMML
- 中文正文、列表和表格
- academic/report/notes 三套模板
- JSON 与文件上传
- 文件过大、无效模板、无效编码、Pandoc 缺失和转换失败
- 一次性下载与下载后删除

### Frontend

```bash
cd frontend
npm run typecheck
npm run build
```

## 9. 完成门槛

- 页面同时支持粘贴和 Markdown 文件上传
- 三套模板可选且实际影响 DOCX
- DOCX 在 Word 中可打开，数学公式、中文与模板样式正确
- 下载后任务文件被删除，未下载文件按 TTL 清理
- API 不直接调用 shell，不记录用户正文
- 后端测试、前端类型检查和构建全部通过
- Docker Compose 定义可解析并包含 frontend/backend 健康检查

## 10. 验证记录

- Backend：29 个 pytest 测试通过；包含真实 Pandoc API、公开示例和安全回归用例。
- DOCX：标题、列表、表格、中文、三套模板及 Word 原生 OMML 公式通过结构检查。
- Word：`docs/tests/mvp-e2e.docx` 在 Microsoft Word 16.0 中正常打开并完成一页视觉验收。
- Frontend：`vue-tsc -b` 与 Vite 生产构建通过。
- Docker：Compose YAML 结构与服务依赖通过静态校验；当前验证机没有 Docker CLI，尚未执行镜像构建和容器冷启动。
- 测试环境有一条来自 FastAPI/Starlette `TestClient` 的上游弃用警告，不影响测试结果或运行服务。
