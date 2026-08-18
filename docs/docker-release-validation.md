# AI2Doc Docker Release Validation

> 状态：Pending。此文件先冻结 Milestone 1.95 的验证方法；只有干净 Runner、DOCX artifact 和视觉检查全部完成后才给出发布结论。

## 1. Environment

当前开发机没有 Docker、Docker Compose 或 Podman。为避免把静态检查写成冷启动成功，本里程碑使用 GitHub 托管的全新 `ubuntu-24.04` Runner，检出公开仓库后执行真实 Docker Compose 流程。

待记录：

- Runner OS
- Docker Engine 版本
- Docker Compose 版本
- 被验证的 Commit SHA

## 2. Build Result

待执行：

```bash
docker compose build --pull
```

必须确认 frontend 和 backend 镜像均成功构建，并记录构建耗时。

## 3. Runtime Result

待执行并记录：

```bash
docker compose up --detach --wait
docker compose ps
```

通过 `http://localhost:8080` 验证 frontend、Nginx 反向代理、backend readiness 与页面内容。仓库 Compose 的公开端口是 `8080`，因此本报告使用 README 中的实际入口，而不是未映射的端口 80。

## 4. E2E Result

使用 [`../examples/docker-release-example.md`](../examples/docker-release-example.md) 和 Academic 模板完成真实转换。自动化门禁必须检查：

- 页面和 readiness 返回 HTTP 200，且 Headless Chrome 真实完成粘贴、Academic 选择、Generate DOCX 和下载链接展示
- 转换与 DOCX 下载成功
- 第二次下载返回 404
- DOCX ZIP/OOXML 结构完整
- 中文、Word 表格和原生 OMML 公式存在
- Academic 页眉页脚存在，证明 reference DOCX 生效
- 下载的 DOCX artifact 可以被渲染，并完成逐页视觉检查

## 5. Restart Result

待执行：

```bash
docker compose down
docker compose up --detach --wait
```

重启后必须再次通过 readiness、首页访问和容器状态检查。

## 6. Conclusion

Pending。当前不得发布 `v0.1.0`，也不得把 GitHub Workflow 的存在视为 Docker 门禁通过。最终结论将在真实运行与 DOCX 视觉验收后更新。
