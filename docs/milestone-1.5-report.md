# AI2Doc Milestone 1.5 Report

## 1. Executive summary

Milestone 1.5 completed the repository-side work required for an open-source release candidate without adding product features.

The local development path is verified end to end: frontend, backend readiness, Nginx-equivalent Vite proxy, real Pandoc conversion, browser download, one-time token rejection and Word rendering. GitHub automation, community templates, public examples, real screenshots, security documentation and dependency audits are in place.

Two external release gates remain open:

1. This machine has no Docker/Compose runtime, so images have not been built or cold-started.
2. The repository has no Git remote, so workflow definitions have not yet executed on GitHub and the README still uses a generic `<REPOSITORY_URL>` placeholder.

AI2Doc is therefore a **release candidate**, not yet a verified `v0.1.0` release.

## 2. Docker status

| Item | Status |
| --- | --- |
| Compose YAML parsing | Passed |
| Frontend/backend service topology | Passed by static review |
| Backend non-root user and tmpfs | Passed by static review |
| Pandoc checksum verification | Present |
| `docker compose build` | Blocked: Docker CLI unavailable |
| `docker compose up` | Blocked: Docker CLI unavailable |
| Container health and Nginx proxy | Not executed |

Full environment evidence and exact retest commands are recorded in [`docker-validation.md`](docker-validation.md).

## 3. CI status

Added:

- `.github/workflows/backend-test.yml`
- `.github/workflows/frontend-test.yml`

Backend workflow:

- Ubuntu 24.04
- Python 3.12, 3.13 and 3.14 matrix
- checksum-verified Pandoc 3.9.0.2
- locked dependency installation
- complete pytest suite

Frontend workflow:

- Ubuntu 24.04
- Node.js 24
- lockfile-based `npm ci`
- TypeScript check
- production Vite build

Both workflows use read-only repository permissions, timeouts, dependency caching and cancellation of superseded branch runs. All workflow/Issue YAML files parse locally. Actual GitHub Actions status is pending repository publication and push.

## 4. Open-source readiness

Completed assets:

- structured Bug and Feature Issue forms
- Pull Request checklist covering scope, tests, API compatibility and privacy
- `SECURITY.md` with private reporting guidance and MVP boundaries
- updated `CONTRIBUTING.md`
- README with three-minute Docker path, architecture, limitations and real screenshots
- public synthetic examples for formulas, reports and Chinese content
- real Web, template selection and Word output screenshots under `docs/images/`

The README clone command intentionally uses `<REPOSITORY_URL>` because no Git remote exists. It must be replaced with the actual repository URL before public release.

## 5. Validation results

| Check | Result |
| --- | --- |
| Backend pytest suite | 29 passed |
| Real Pandoc public examples | Math, report and Chinese passed |
| Frontend TypeScript | Passed |
| Frontend production build | Passed |
| Local browser page load | Passed |
| Browser text → report template → generation | Passed |
| Browser DOCX download | Passed |
| Second use of download token | 404, passed |
| Browser console errors/warnings | None |
| Word 16.0 opens public report output | Passed, one page |
| `npm audit --audit-level=high` | 0 vulnerabilities |
| `pip-audit` after pip tool upgrade | No known vulnerabilities |
| Docker cold start | Not run; environment blocked |
| GitHub-hosted workflow run | Not run; repository has no remote |

## 6. Security decision

The local MVP conversion path has appropriate controls for input size, encoding, template/path safety, shell avoidance, Pandoc sandboxing, output size, timeouts, one-time downloads and temporary-file cleanup.

It is not approved for direct unauthenticated public-internet exposure. Rate limiting, conversion concurrency limits, container CPU/memory limits and deployment monitoring are release-environment requirements. Details are in [`security-review.md`](security-review.md).

## 7. Known limitations

- Docker backend currently targets `linux/amd64`; ARM uses emulation.
- Download tokens and metadata live in one backend process; multi-worker deployment is unsupported.
- No authentication, rate limiting, persistent history or cloud storage.
- Direct chunked uploads to FastAPI do not receive the same early body-size enforcement as normal Nginx/Compose traffic.
- Formula support covers the tested common LaTeX subset, not every LaTeX package or macro.
- GitHub repository URL, workflow badges and first hosted runs are unavailable until a remote is configured.

## 8. Recommendation

Do not add product features yet. Before tagging `v0.1.0`:

1. Create or connect the GitHub repository and replace `<REPOSITORY_URL>` in the README.
2. Push the branch and require both GitHub Actions workflows to pass.
3. Run the documented Docker cold-start test on a clean amd64 machine.
4. Generate a DOCX through port 8080, verify Word output and confirm cleanup.
5. Record the results in `docker-validation.md`, then tag the release.

After those gates pass, publish `v0.1.0`, collect real user feedback and use that evidence to choose the next product milestone.
