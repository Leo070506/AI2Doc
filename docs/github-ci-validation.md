# AI2Doc GitHub CI Validation

> 状态：Passed。首次 GitHub 托管 Backend 与 Frontend CI 均由 `push` 自动触发并成功完成。

## 1. Scope

本报告只记录 GitHub Actions 的真实运行结果。工作流 YAML 本地可解析不等于 GitHub Runner 执行成功。

待验证工作流：

- `.github/workflows/backend-test.yml`
- `.github/workflows/frontend-test.yml`

## 2. Local preflight

本地验证日期：2026-08-14

GitHub 托管验证日期：2026-08-18

| Check | Result |
| --- | --- |
| Workflow YAML parse | Passed locally |
| Workflow repository permission | `contents: read` |
| Backend local pytest | Passed; 29 tests |
| Frontend local typecheck | Passed |
| Frontend local production build | Passed |
| Git remote | `https://github.com/Leo070506/AI2Doc.git` |
| GitHub-hosted run | Passed |

## 3. Hosted acceptance criteria

托管结果：

| Workflow | Result |
| --- | --- |
| Backend / Python 3.12 | Success |
| Backend / Python 3.13 | Success |
| Backend / Python 3.14 | Success |
| Frontend / npm ci | Success |
| Frontend / TypeScript | Success |
| Frontend / production build | Success |

Backend 的 checkout、Python 安装、Pandoc 3.9.0.2 校验安装、依赖安装和 pytest 在三个 Python 版本上全部成功。Frontend 的 checkout、Node.js、`npm ci`、TypeScript 检查和生产构建全部成功。

## 4. Hosted evidence

- Repository URL：`https://github.com/Leo070506/AI2Doc`
- Commit SHA：`509d50cdabae67ba00c6d37090dec989977636ef`
- Backend run：[32135542494](https://github.com/Leo070506/AI2Doc/actions/runs/32135542494)
- Frontend run：[32135542460](https://github.com/Leo070506/AI2Doc/actions/runs/32135542460)
- Event：`push`
- Runner：`ubuntu-24.04`
- Frontend completed：2026-08-18 12:12:03 UTC（20:12:03 Asia/Shanghai）
- Backend completed：2026-08-18 12:12:25 UTC（20:12:25 Asia/Shanghai）
- Final result：Passed

## 5. Trigger note

空仓库的首次 Push 注册了两份 active workflow，但没有生成 check suite。随后对两份 workflow 增加 `run-name` 并通过正常 `push` 事件提交；该 Push 自动创建了 Backend 和 Frontend 两个运行。未使用 `workflow_dispatch`，因此“自动触发”验收通过。

GitHub CI 门禁已经关闭。`v0.1.0` 仍不得发布，直到独立的 Docker 冷启动与浏览器 → DOCX 端到端验收通过。
