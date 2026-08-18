# AI2Doc Docker Release Validation

> 状态：**Passed**。Milestone 1.95 的 Docker 冷启动、真实浏览器转换、DOCX 检查与重启门禁均已通过；本阶段未创建 `v0.1.0` Release。

## 1. Environment

当前开发机未安装 Docker、Docker Compose 或 Podman。为保证结果来自不含 AI2Doc 开发环境的机器，本次验证使用 GitHub 托管的全新 `ubuntu-24.04` Runner，对公开仓库的 `main` 提交执行真实 Docker Compose 流程。

最终通过记录：

- Workflow：[Docker release gate · run 32138709346](https://github.com/Leo070506/AI2Doc/actions/runs/32138709346)
- Commit：`0a6a1678cb224fc9b17044c57df05591d88bd8eb`
- Runner OS：Ubuntu 24.04.4 LTS，Linux 6.17.0-1022-azure，x86_64
- Docker Engine：28.0.4
- Docker Compose：v2.38.2
- Google Chrome：151.0.7922.108
- Pandoc：3.9.0.2

GitHub Runner 每次从空白托管环境检出同一公开提交，因此没有复用作者机器的依赖、镜像或 AI2Doc 工作目录。

## 2. Build Result

执行：

```bash
docker compose build --pull
```

结果：**Passed**。

- frontend image：构建成功
- backend image：构建成功，Pandoc 可从容器 `PATH` 正常执行
- 缺失依赖：无
- 完整构建耗时：19 秒

## 3. Runtime Result

执行：

```bash
docker compose up --detach --wait
docker compose ps
```

结果：**Passed**。

- `ai2doc-backend-1`：running、healthy
- `ai2doc-frontend-1`：running、healthy
- Nginx：在 frontend 容器内正常提供静态页面并代理 `/api`
- backend readiness：HTTP 200，Pandoc `available`
- 模板发现：`academic`、`notes`、`report`
- 页面入口：[http://localhost:8080](http://localhost:8080)

仓库 Compose 的公开端口是 `8080`，因此实际入口不是未映射的端口 80。

## 4. E2E Result

使用 [`../examples/docker-release-example.md`](../examples/docker-release-example.md) 和 Academic 模板完成真实转换。Headless Chrome 实际执行了页面输入、Academic 选择和 **Generate DOCX** 点击，并等待网页展示一次性下载链接。

结果：**Passed**。

- 首页：HTTP 200
- 浏览器转换：成功，页面显示 `Your document is ready.`
- 页面下载文件名：`AI2Doc_Report.docx`
- API 转换：HTTP 200
- DOCX 下载：HTTP 200，12,468 bytes
- 同一令牌第二次下载：HTTP 404，证明一次性下载与删除生效
- DOCX ZIP/OOXML：结构完整
- 中文文本：存在且可正常显示
- 数学公式：1 个 Word 原生 OMML 公式，不是图片
- Word 表格：1 个
- Academic 模板：`word/header1.xml` 与 `word/footer1.xml` 均存在

最终 DOCX 另在 Microsoft Word 16.0 中以只读方式实际打开并导出 PDF：

- 验证主机：Microsoft Windows 10.0.26200
- 页数：1
- 段落：15
- 表格：1
- Word 原生公式：1
- 视觉检查：中文、公式、表格、Academic 页眉页脚均正常；无乱码、截断、重叠或缺失内容

Runner 的 Chrome 截图中中文输入显示为方框，是 GitHub Ubuntu 浏览器环境未提供中文字体字形所致；DOCX 内部中文检查和 Microsoft Word 实际渲染均通过，因此不属于生成文档缺陷。

## 5. Restart Result

执行：

```bash
docker compose down
docker compose up --detach --wait
```

结果：**Passed**。

- frontend：重新启动后 healthy，首页 HTTP 200
- backend：重新启动后 healthy，readiness HTTP 200
- Nginx 代理：重新启动后正常

## 6. Issues Found and Fixed

冷启动门禁在全新 Linux 环境发现并修复了三个真实部署问题：

| 问题 | 根因 | 修复 |
|---|---|---|
| backend 无法写入临时目录 | tmpfs 默认属主与非 root 容器用户不匹配 | 固定 backend UID/GID，并为 tmpfs 设置相同属主与权限 |
| readiness 报 Pandoc 不可用 | Compose 固定了不存在的 `/usr/local/bin/pandoc` | 改为从容器 `PATH` 解析 `pandoc` |
| frontend 被判定 unhealthy | healthcheck 使用 `localhost` 时解析行为不稳定 | healthcheck 固定访问 `127.0.0.1:8080` |

相应修复均由后续干净 Runner 重新构建并验证，没有通过跳过 healthcheck 或放宽断言来掩盖问题。

## 7. Conclusion

**AI2Doc 已满足 v0.1.0 的 Docker 发布门禁。**

已验证闭环：

```text
公开仓库检出
  → Docker Compose 构建
  → frontend / backend / Nginx 启动
  → 浏览器输入 Markdown 并选择 Academic
  → 生成并下载 DOCX
  → Microsoft Word 打开与视觉检查
  → Docker Compose 停止并重新启动
```

本报告只确认技术发布门禁通过。按 Milestone 1.95 约束，未创建 tag，也未创建 GitHub Release；`v0.1.0` 仍保持 `Unreleased`，等待下一步指令。
