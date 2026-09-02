import assert from "node:assert/strict";
import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const dir = await mkdtemp(path.join(tmpdir(), "claude-model-sync-"));
const manifest = path.join(dir, "models.json");
await writeFile(manifest, JSON.stringify({ models: [
  { alias: "claude-visible", target: "real-visible", visible: true },
  { alias: "claude-hidden", target: "real-hidden", visible: false }
] }));
const port = 18787 + Math.floor(Math.random() * 1000);
const child = spawn(process.execPath, [path.resolve("proxy/server.mjs")], {
  env: { ...process.env, PORT: String(port), CLAUDE_MODEL_SYNC_MANIFEST: manifest, LOCAL_CLIENT_TOKEN: "test-client-token" },
  stdio: ["ignore", "pipe", "inherit"]
});

try {
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("proxy start timeout")), 5000);
    child.stdout.on("data", (chunk) => {
      if (chunk.toString().includes('"event":"listening"')) { clearTimeout(timer); resolve(); }
    });
    child.on("exit", (code) => reject(new Error(`proxy exited ${code}`)));
  });
  const health = await fetch(`http://127.0.0.1:${port}/healthz`);
  assert.equal(health.status, 200);
  const unauthorized = await fetch(`http://127.0.0.1:${port}/v1/models`);
  assert.equal(unauthorized.status, 401);
  const listed = await fetch(`http://127.0.0.1:${port}/v1/models`, { headers: { authorization: "Bearer test-client-token" } });
  const payload = await listed.json();
  assert.deepEqual(payload.data.map((row) => row.id), ["claude-visible"]);
  console.log("proxy tests passed");
} finally {
  child.kill("SIGTERM");
}
