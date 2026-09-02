# Claude Model Sync

一个面向 Claude Desktop/Cowork、Claude Code、OpenClaw 和本地 Gateway 的可移植模型目录同步及严格别名代理工具。

首个版本从已验证的 Windows 个人工作流中提取确定性核心，同时删除个人路径、固定模型数量、端口、应用 ID、UUID、Provider 地址和凭据。它**不宣称**完整模拟 Claude 协议。

## 主要能力

- 从内联/本地 JSON、YAML 或 OpenAI 兼容 `/v1/models` 动态获取模型目录；
- 自动生成 `claude-*` 别名并阻止冲突和重复；
- 分离可见菜单模型与隐藏兼容别名；
- 提供 `inspect`、`plan`、`apply`、`verify`、`rollback`；
- 默认不删除旧模型，只有显式 `--prune` 才会清理；
- 原子写入、备份、事务记录、幂等应用和回滚；
- 严格 Alias Proxy：默认回环地址、可选本地认证、路径白名单、请求体限制、超时、窄 CORS、取消上游请求、健康检查和结构化日志；
- Windows `.reg` 生成器、实验性 Linux 用户服务模板、OpenClaw Agent Skill、跨平台 CI 和 Gitleaks。

## 快速开始

```bash
python -m pip install -e .
claude-model-sync inspect --config examples/config.json
claude-model-sync plan --config examples/config.json
claude-model-sync apply --config examples/config.json --yes
claude-model-sync verify --config examples/config.json
```

自动化可使用 JSON 输出：

```bash
claude-model-sync --json plan --config examples/config.json
```

删除旧模型必须明确指定：

```bash
claude-model-sync plan --config config.json --prune
claude-model-sync apply --config config.json --prune --yes
```

## 平台边界

- Windows：CLI/Proxy 与注册表文件生成；导入注册表和重启应用仍需人工审查。
- macOS：CLI/Proxy 可用；mobileconfig、LaunchAgent 和 MDM 写入仍属实验性/待实现。
- Linux：CLI/Proxy 与 systemd user 模板；不宣称支持 Claude Desktop 下拉菜单。

详见 [references/platforms.md](references/platforms.md)。

## 配置与凭据

JSON 不需要第三方依赖；YAML 需要：

```bash
python -m pip install -e ".[yaml]"
```

远端 Token 只能通过配置中的环境变量**名称**引用，例如 `tokenEnv: MODEL_GATEWAY_TOKEN`。不要把真实值写入配置、命令、日志或仓库。

## 严格代理

代理仅替换请求体的 `model`、返回可见模型列表并转发 `/v1/messages`；不会修改 Prompt、Tools、Thinking、Metadata 或响应内容。运行前通过受保护环境配置 `CLAUDE_MODEL_SYNC_MANIFEST`、`UPSTREAM_BASE_URL`，并建议配置 `LOCAL_CLIENT_TOKEN`。

## Windows 菜单文件

```powershell
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Output ./generated/claude-models.reg
```

脚本只生成供审查的 `.reg` 文件，不会自动导入。导入前请备份 `HKCU\Software\Policies\Claude`。

## 测试

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q src tests
node --check proxy/server.mjs
node tests/test_proxy.mjs
```

安全政策见 [SECURITY.md](SECURITY.md)，许可证为 MIT。
