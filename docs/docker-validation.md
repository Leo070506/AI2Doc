# AI2Doc Docker Validation

## 1. Validation scope

Milestone 1.5 的目标是验证陌生开发者能否通过以下路径启动 AI2Doc：

```text
git clone
→ docker compose build
→ docker compose up
→ open http://localhost:8080
→ generate and download DOCX
```

只有真实执行过的步骤才记录为通过。YAML 解析成功不等同于镜像能够构建或容器能够启动。

## 2. Environment

验证日期：2026-08-14

| Item | Value |
| --- | --- |
| OS | Microsoft Windows NT 10.0.26200.0 |
| PowerShell | 7.6.4 |
| Python | 3.12.13 |
| Node.js | 24.16.0 |
| Pandoc | 3.9.0.2 portable validation copy |
| Docker CLI | unavailable |
| Docker Compose | unavailable because Docker CLI is absent |
| Podman fallback | unavailable |

## 3. Commands and results

| Check | Result | Evidence |
| --- | --- | --- |
| Locate `docker` | blocked | No executable is available on PATH |
| Read Compose version | blocked | Requires Docker CLI |
| Parse `docker-compose.yml` | passed | YAML loads successfully and defines `frontend` and `backend` |
| `docker compose build` | not run | Environment does not provide a container runtime |
| `docker compose up` | not run | Environment does not provide a container runtime |
| Backend container health | not run | Requires running containers |
| Nginx proxy in container | not run | Requires running containers |
| Browser access through port 8080 | not run | Requires running containers |

## 4. Static review completed

- Compose defines separate frontend and backend services.
- Frontend waits for the backend readiness health check.
- Backend uses a memory-backed `tmpfs` for `/tmp/ai2doc`.
- Backend runs as a non-root user.
- Pandoc 3.9.0.2 download is checksum-verified during image build.
- Nginx proxies `/api/` and `/health/` to the backend and limits request bodies.
- Only the frontend publishes a host port (`8080`).
- The backend is pinned to `linux/amd64` because its Pandoc Debian artifact is architecture-specific.

## 5. Blocking condition and follow-up

The current environment cannot satisfy the real Docker cold-start gate. This is an environment limitation, not a passing result.

Before tagging `v0.1.0`, run the following on a clean machine with Docker Engine and Compose v2:

```bash
docker compose build --pull
docker compose up --detach --wait
curl --fail http://localhost:8080/health/ready
```

Then submit `examples/report-example.md`, download the DOCX, confirm the second download attempt fails, and run:

```bash
docker compose down --volumes
```

Record the Docker/Compose versions, build duration, container health, HTTP result, generated DOCX inspection, cleanup result, and any architecture-specific behavior in this document.
