# AI2Doc Docker End-to-End Validation

> 状态：当前机器没有 Docker/Compose，真实冷启动尚未执行。

## 1. Release gate

`v0.1.0` 发布前必须在干净、支持 `linux/amd64` 容器的环境完成：

```text
git clone
→ docker compose up --build
→ frontend + backend healthy
→ browser opens localhost:8080
→ Markdown converts and downloads
→ DOCX opens correctly
→ temporary file is deleted
```

静态配置检查、本地 Vite/FastAPI 测试和宿主机 Pandoc 转换不能替代此项验证。

## 2. Current environment

验证日期：2026-08-14

| Item | Value |
| --- | --- |
| OS | Microsoft Windows NT 10.0.26200.0 |
| Docker CLI | Unavailable |
| Docker Compose | Unavailable |
| Podman fallback | Unavailable |
| Result | Blocked by missing container runtime |

更早的环境与静态审查记录见 [`docker-validation.md`](docker-validation.md)。

## 3. Clean-environment procedure

在没有本项目镜像、容器和卷缓存的验证机上执行：

```bash
git clone <REPOSITORY_URL> AI2Doc
cd AI2Doc
docker compose version
docker compose build --pull
docker compose up --detach --wait
curl --fail http://localhost:8080/health/ready
```

随后在浏览器打开 `http://localhost:8080`：

1. 上传 `examples/report-example.md`。
2. 选择 Report 模板。
3. 点击 Generate DOCX 并下载。
4. 用 Microsoft Word 或兼容软件打开文件。
5. 确认标题、列表、表格、中文和样式正常。
6. 确认同一下载地址第二次访问返回 `404`。

最后收集日志并停止服务：

```bash
docker compose ps
docker compose logs --no-color
docker compose down --volumes
```

## 4. Acceptance matrix

| Check | Status | Evidence |
| --- | --- | --- |
| Docker/Compose versions recorded | Pending | — |
| Images build from clean cache | Pending | — |
| Backend reaches healthy state | Pending | — |
| Frontend starts on port 8080 | Pending | — |
| Nginx proxies `/health` and `/api` | Pending | — |
| Browser conversion succeeds | Pending | — |
| Downloaded DOCX opens correctly | Pending | — |
| One-time download returns 404 on reuse | Pending | — |
| Containers stop cleanly | Pending | — |

## 5. Evidence to record

- Validation OS and architecture：待填写
- Docker Engine version：待填写
- Docker Compose version：待填写
- Commit SHA：待填写
- Build duration：待填写
- Container status：待填写
- Generated document inspection：待填写
- Logs/issues：待填写
- Final result：待填写

本矩阵全部通过后，才能把 Docker 冷启动质量门禁标记为完成。
