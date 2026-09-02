import http from "node:http";
import { readFile } from "node:fs/promises";

const host = process.env.HOST || "127.0.0.1";
const port = Number(process.env.PORT || 8787);
const manifestPath = process.env.CLAUDE_MODEL_SYNC_MANIFEST;
const upstream = (process.env.UPSTREAM_BASE_URL || "").replace(/\/$/, "");
const upstreamKey = process.env.UPSTREAM_API_KEY || "";
const clientToken = process.env.LOCAL_CLIENT_TOKEN || "";
const allowedOrigin = process.env.ALLOWED_ORIGIN || "";
const maxBody = Number(process.env.MAX_BODY_BYTES || 2_000_000);
const timeoutMs = Number(process.env.UPSTREAM_TIMEOUT_MS || 120_000);
const allowed = new Set(["/v1/messages"]);

function log(event, fields = {}) {
  process.stdout.write(JSON.stringify({ ts: new Date().toISOString(), event, ...fields }) + "\n");
}

async function catalog() {
  if (!manifestPath) throw new Error("CLAUDE_MODEL_SYNC_MANIFEST is required");
  const data = JSON.parse(await readFile(manifestPath, "utf8"));
  return data.models || [];
}

function send(res, status, body, origin = "") {
  const headers = { "content-type": "application/json; charset=utf-8" };
  if (allowedOrigin && origin === allowedOrigin) headers["access-control-allow-origin"] = origin;
  res.writeHead(status, headers);
  res.end(JSON.stringify(body));
}

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > maxBody) throw Object.assign(new Error("request body too large"), { status: 413 });
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

const server = http.createServer(async (req, res) => {
  const started = Date.now();
  const path = new URL(req.url, `http://${req.headers.host || "localhost"}`).pathname;
  try {
    if (path === "/healthz") return send(res, 200, { ok: true });
    if (path === "/readyz") {
      await catalog();
      return send(res, upstream ? 200 : 503, { ok: Boolean(upstream) });
    }
    if (clientToken && req.headers.authorization !== `Bearer ${clientToken}`) return send(res, 401, { error: "unauthorized" });
    const models = await catalog();
    if (path === "/v1/models" && req.method === "GET") {
      return send(res, 200, { object: "list", data: models.filter((m) => m.visible).map((m) => ({ id: m.alias, object: "model" })) }, req.headers.origin);
    }
    if (!allowed.has(path) || req.method !== "POST") return send(res, 404, { error: "not_found" });
    if (!upstream) return send(res, 503, { error: "upstream_not_configured" });
    const body = JSON.parse(await readBody(req));
    const match = models.find((m) => m.alias === body.model);
    if (!match) return send(res, 400, { error: "unknown_model_alias" });
    body.model = match.target;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(new Error("upstream timeout")), timeoutMs);
    res.on("close", () => {
      if (!res.writableEnded) controller.abort(new Error("client disconnected"));
    });
    const headers = { "content-type": "application/json", accept: req.headers.accept || "application/json" };
    if (upstreamKey) headers.authorization = `Bearer ${upstreamKey}`;
    let response;
    try {
      response = await fetch(upstream + path, { method: "POST", headers, body: JSON.stringify(body), signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
    res.writeHead(response.status, Object.fromEntries([...response.headers].filter(([key]) => ["content-type", "cache-control"].includes(key.toLowerCase()))));
    if (response.body) for await (const chunk of response.body) res.write(chunk);
    res.end();
    log("request", { path, status: response.status, durationMs: Date.now() - started });
  } catch (error) {
    const status = error.status || (error.name === "AbortError" ? 504 : 500);
    log("error", { path, status, message: error.message });
    if (!res.headersSent) send(res, status, { error: status === 500 ? "internal_error" : error.message }); else res.destroy();
  }
});

server.listen(port, host, () => log("listening", { host, port }));
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => server.close(() => process.exit(0)));
