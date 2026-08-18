# AI2Doc v0.1.0 Release Validation

> 状态：**Passed**。AI2Doc `v0.1.0` 已作为公开、非预发布版本发布；本阶段未增加产品功能。

## Release

- Release title：`AI2Doc v0.1.0`
- Tag：`v0.1.0`
- Tag 类型：annotated tag
- Tag message：`AI2Doc v0.1.0 - First public release`
- Tag object SHA：`990c146166d3eaf34a9362fbc024fae6d92aa34c`
- Release commit SHA：`b5a18f7c582831ec2727072cc12708944ce59c03`
- 发布时间：2026-08-18 13:09:57 UTC（2026-08-18 21:09:57 Asia/Shanghai）
- Release URL：[AI2Doc v0.1.0](https://github.com/Leo070506/AI2Doc/releases/tag/v0.1.0)
- Draft：否
- Prerelease：否

## CI Status

Tag 对应的发布提交自动触发了新一轮 GitHub Actions，结果全部通过：

| Gate | Result | Run |
|---|---|---|
| Backend CI | Passed | [32140733905](https://github.com/Leo070506/AI2Doc/actions/runs/32140733905) |
| Frontend CI | Passed | [32140733892](https://github.com/Leo070506/AI2Doc/actions/runs/32140733892) |
| Docker release gate | Passed | [32140734010](https://github.com/Leo070506/AI2Doc/actions/runs/32140734010) |

三个 Workflow 验证的 head SHA 均为 `b5a18f7c582831ec2727072cc12708944ce59c03`，与 `v0.1.0` 指向的发布提交一致。

## Docker Status

发布前门禁已经确认：

- 干净 Ubuntu Runner 构建 frontend 与 backend 镜像成功
- frontend、backend 与 Nginx 正常启动
- 真实浏览器完成 Markdown 输入、Academic 模板选择和 DOCX 生成
- DOCX 下载、中文、表格、Word 原生 OMML 公式和模板均通过
- Microsoft Word 16.0 实际打开与逐页视觉检查通过
- `docker compose down` 后重新启动通过

完整证据见 [`docker-release-validation.md`](docker-release-validation.md)。

## Public Usage

公开仓库支持以下启动流程：

```bash
git clone https://github.com/Leo070506/AI2Doc.git
cd AI2Doc
docker compose up --build
```

启动后访问 [http://localhost:8080](http://localhost:8080)。

## Repository Check

- GitHub Repository：Public
- `v0.1.0` tag：存在
- `v0.1.0` Release：存在，并设为最新公开版本
- README：包含最新 Release badge、正确版本链接和端口 `8080`
- Changelog：`0.1.0` 已固定发布日期 `2026-08-18`
- README 图片与本地文档链接：通过

## Conclusion

AI2Doc `v0.1.0` 的 tag、GitHub Release、CI、Docker 与公开使用说明均通过最终检查。首个公开版本发布完成；后续功能开发应等待下一阶段规划。
