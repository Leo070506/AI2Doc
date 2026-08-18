# AI2Doc GitHub CI Validation

> 状态：等待 GitHub 仓库地址与首次 Push，尚未通过托管 Runner 验证。

## 1. Scope

本报告只记录 GitHub Actions 的真实运行结果。工作流 YAML 本地可解析不等于 GitHub Runner 执行成功。

待验证工作流：

- `.github/workflows/backend-test.yml`
- `.github/workflows/frontend-test.yml`

## 2. Local preflight

验证日期：2026-08-14

| Check | Result |
| --- | --- |
| Workflow YAML parse | Passed locally |
| Workflow repository permission | `contents: read` |
| Backend local pytest | Passed; 29 tests |
| Frontend local typecheck | Passed |
| Frontend local production build | Passed |
| Git remote | Pending; no `origin` configured |
| GitHub-hosted run | Not started |

## 3. Hosted acceptance criteria

首次 Push 后必须确认：

| Workflow | Required result |
| --- | --- |
| Backend / Python 3.12 | Success |
| Backend / Python 3.13 | Success |
| Backend / Python 3.14 | Success |
| Frontend / npm ci | Success |
| Frontend / TypeScript | Success |
| Frontend / production build | Success |

不允许忽略 dependency、权限、缓存、Pandoc 下载或环境兼容错误。任何失败都应先修复并重新运行，再创建标签。

## 4. Evidence to record after Push

- Repository URL：待填写
- Commit SHA：待填写
- Backend run URL / run ID：待填写
- Frontend run URL / run ID：待填写
- Runner OS：待填写
- Completion time：待填写
- Final result：待填写

只有所有矩阵任务和前端任务均为绿色时，本报告才能改为“Passed”。
