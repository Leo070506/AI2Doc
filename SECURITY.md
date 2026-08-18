# Security Policy

## Supported versions

AI2Doc has not published its first release yet. Security fixes currently target the default branch. A supported-version table will be added with `v0.1.0`.

## Reporting a vulnerability

Do not open a public Issue for suspected vulnerabilities or attach private documents, tokens, local paths, or user conversations.

After the repository is published, use the repository's **Security → Report a vulnerability** private advisory form. Maintainers should acknowledge a complete report within seven days and coordinate disclosure after a fix is available. This project does not currently offer a bug bounty.

Include:

- affected version or commit
- impact and prerequisites
- minimal reproduction using synthetic content
- relevant configuration without secrets
- suggested mitigation, if known

## MVP security boundaries

- AI2Doc accepts UTF-8 Markdown text or `.md`/`.markdown` uploads only.
- Inputs and outputs have byte limits and Pandoc conversions have a timeout.
- Template IDs map to three server-controlled reference DOCX files.
- Pandoc is invoked with an argument array, `shell=False`, and sandbox mode.
- User content is stored in isolated temporary directories and is deleted after download; TTL cleanup handles abandoned files.
- The MVP has no authentication, rate limiting, database, cloud storage, or multi-instance coordination. Do not expose it directly to the public internet without an HTTPS reverse proxy, request-rate controls, concurrency limits, and deployment-specific monitoring.
