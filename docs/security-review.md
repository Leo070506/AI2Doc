# AI2Doc Milestone 1.5 Security Review

## 1. Scope

Review date: 2026-08-14

Reviewed surfaces:

- JSON text and multipart Markdown upload
- template selection and server-side paths
- Pandoc subprocess construction
- temporary input/output lifecycle
- one-time download tokens
- frontend/backend dependency manifests
- Docker and Nginx boundaries

This is an engineering review for the MVP, not a penetration test or security certification.

## 2. Controls verified

| Area | Control | Result |
| --- | --- | --- |
| Input size | 1 MiB application limit plus Content-Length early rejection | Passed |
| Upload type | Only `.md` and `.markdown`; UTF-8/UTF-8 BOM decoding | Passed |
| Output size | 10 MiB maximum generated DOCX | Passed |
| Template path | `academic`, `report`, `notes` whitelist only | Passed |
| Upload filename | Never used to construct storage paths | Passed |
| Workspace path | High-entropy child directory under configured storage root | Passed |
| Pandoc invocation | Argument array, `shell=False`, fixed flags, sandbox and timeout | Passed |
| User-controlled flags | No request field can add Pandoc options, filters or reference files | Passed |
| Download | High-entropy token, single claim, fixed output filename | Passed |
| Response safety | Fixed user-facing errors; no stderr, command, stack or absolute path | Passed |
| Cleanup | Input deleted after conversion; output deleted after response; TTL fallback | Passed |
| Container process | Backend runs as a non-root user | Passed by static Dockerfile review |
| Public exposure | Backend has no published host port in Compose | Passed by static Compose review |

Automated security regression tests cover traversal-like template IDs, hostile upload filenames, argument-array invocation, `shell=False`, Pandoc sandbox mode, size limits, invalid encodings, one-time downloads and failure cleanup.

## 3. Dependency audit

### Frontend

`npm audit --audit-level=high` completed successfully:

```text
found 0 vulnerabilities
```

### Backend

`pip-audit 2.10.1` found vulnerabilities only in the local environment's old `pip 25.0.1`, not in AI2Doc runtime libraries. The environment was upgraded to `pip 26.2.1`; a second audit returned:

```text
No known vulnerabilities found
```

The backend image now upgrades and pins pip 26.2.1 before installing runtime requirements.

## 4. Residual risks and release requirements

| Risk | Current mitigation | Required before public internet exposure |
| --- | --- | --- |
| Request flooding / Pandoc process exhaustion | Input/output limits and 30-second timeout | Reverse-proxy rate limit, application concurrency bound and container CPU/memory limits |
| Oversized chunked multipart body sent directly to FastAPI | Post-read byte check; Nginx limits normal Compose traffic to 2 MiB | Do not expose backend directly; add ASGI-level streaming/request limit if direct exposure is needed |
| Multi-worker or multi-instance downloads | Single-process in-memory token registry | Keep one backend worker for MVP or introduce shared metadata/storage before scaling |
| Container supply-chain drift | Pandoc artifact checksum and pinned application dependencies | Pin base images by digest and enable automated image scanning |
| Native ARM container support | Backend fixed to `linux/amd64` | Build and validate a checksum-pinned arm64 Pandoc image |
| Complex Markdown resource consumption | Pandoc sandbox, byte limits and timeout | Add representative stress tests and operating-system memory limits |
| No authentication | MVP intended for local/trusted trial use | Add deployment access controls before hosting for a private audience |

## 5. Decision

The core conversion path is appropriately constrained for a local/open-source MVP. It is not yet approved for direct unauthenticated public-internet exposure. A `v0.1.0` local Docker release can proceed after real container cold-start validation, repository URL finalization and the release requirements above are acknowledged.
