# AI2Doc 开发计划

## 1. 执行原则

AI2Doc 使用 Documentation First：每个里程碑先冻结范围、接口和验收标准，再实现最小代码，最后用自动化测试、真实 DOCX 和文档更新收口。当前不会开发登录、数据库、AI API、支付、浏览器插件、云存储或社区功能。

## 2. 已完成阶段

### Phase 0 — 项目规划与技术验证

- 建立开源项目文档、目录、贡献规范和 MIT License。
- 确认 Vue 3 + FastAPI + Pandoc + reference DOCX 架构。
- 验证基础 Markdown、中文、表格、原生 Word 数学公式和三套模板。
- 结论见 [`milestone-0-report.md`](milestone-0-report.md)。

### Milestone 1 — Web MVP

已完成最小用户闭环：

```text
paste AI response / upload Markdown
→ choose academic, report, or notes
→ POST /api/convert
→ Pandoc + reference DOCX
→ one-time download
→ delete temporary workspace
```

实现内容：

- Vue 3、TypeScript、Vite、Tailwind CSS 单页应用
- FastAPI 转换、下载、存活和就绪接口
- 保守 Markdown 首尾清理，不调用 AI
- Pandoc 参数数组封装、超时和稳定错误映射
- 1 MiB 输入限制、10 MiB 输出限制和模板白名单
- 下载后删除、失败清理、启动/周期 TTL 清理
- frontend/backend Dockerfile、Nginx 同源代理和 Docker Compose
- 29 个后端测试、前端类型检查/生产构建、Word 视觉验收

已知验证缺口：当前开发机没有 Docker CLI，容器镜像构建和冷启动尚未实际执行；Compose YAML 已通过静态校验。

## 3. 当前质量门禁

每次触及核心转换链路至少运行：

```bash
cd backend
pytest

cd ../frontend
npm run typecheck
npm run build
```

涉及 Pandoc、模板或 DOCX 的变更还必须确认：

- 中文和表格仍保留在 OOXML 中
- 行内/块级数学公式仍为原生 OMML，不是图片
- academic、report、notes 的 reference DOCX 均实际生效
- Word 或兼容软件可以打开代表性输出
- 下载、失败和到期路径不会留下用户文件

## 4. 下一阶段候选（尚未授权）

下一步应优先做发布准备，而不是增加产品功能：

1. 在具备 Docker 的干净环境执行 `docker compose up --build` 冷启动。
2. 加入 CI，运行后端测试和前端构建。
3. 增加基础速率限制、并发上限与部署安全头。
4. 用公开脱敏样例制作真实 README 截图/GIF。
5. 明确首个预发布版本的支持范围与已知限制。

Phase 2 的模板管理、AI 增强、浏览器插件与桌面客户端仍按 [`../ROADMAP.md`](../ROADMAP.md) 排期。本阶段完成后停止，等待下一条开发指令。

## 5. Milestone 1.5 — 开源发布准备（已授权）

范围只包含发布可靠性与展示材料：

1. 记录 Docker 与 Compose 的真实可用性；只有实际构建、启动并完成 HTTP/DOCX 闭环后才标记通过。
2. GitHub Actions 使用只读仓库权限，后端覆盖 Python 3.12、3.13、3.14，前端固定 Node.js 24 并使用锁文件安装。
3. 提供结构化 Bug、功能建议和 Pull Request 模板，降低社区参与门槛。
4. 使用脱敏 Markdown 样例和真实页面/DOCX 截图完善 README。
5. 审计输入限额、扩展名/编码、模板白名单、路径边界、`shell=False`、Pandoc 参数、下载令牌和清理策略。
6. 运行后端测试、前端类型检查/构建、真实 API/DOCX 和截图验收，并在报告中保留已知限制。

不包含：新转换能力、用户系统、数据库、AI API、云服务、浏览器插件或桌面客户端。完成后停止并等待下一条开发指令。

## 6. Milestone 1.9 — v0.1.0 发布准备（已授权）

范围冻结为发布可信度工作，不增加产品能力：

1. 审计首个提交候选，确保忽略本地环境、依赖、缓存和临时用户文件，并排查凭据、个人路径及文档元数据。
2. 创建 `CHANGELOG.md`、Release 草稿、GitHub CI 验收记录和 Docker 端到端验收记录。
3. 在用户提供正式仓库地址后配置 `origin`，推送 `main`，并记录首次 GitHub Actions 的真实结果。
4. 在具备 Docker Compose v2 的干净环境完成镜像构建、容器健康、Nginx 代理、浏览器转换、DOCX 打开和一次性下载验证。
5. 仅当托管 CI 与 Docker 闭环全部通过后创建 `v0.1.0` 标签和 GitHub Release。

未提供 GitHub 仓库地址、Git 作者身份或 Docker 环境时，应保留明确的 Pending 状态，不猜测信息，也不把静态检查写成真实验证。
