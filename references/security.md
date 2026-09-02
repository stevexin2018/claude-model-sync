# Security design

- The proxy binds to `127.0.0.1` unless overridden.
- Set `LOCAL_CLIENT_TOKEN`; localhost alone is not an identity boundary.
- Upstream credentials are read from process environment and never returned or logged.
- Only `/v1/messages`, `/v1/models`, `/healthz`, and `/readyz` are recognized.
- Request size and upstream time are bounded.
- Client disconnects abort upstream work.
- CORS is absent by default and permits only one exact configured origin.
- Logs contain event, status, path, and duration, not bodies or headers.
- Catalog writes are atomic and recorded; OS configuration needs its own backup.

For production, run under a least-privileged user, protect environment files, limit outbound destinations, and rotate any credential that has ever appeared in source history.
