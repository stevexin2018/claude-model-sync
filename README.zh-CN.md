# Claude Model Sync

一个面向 Claude Desktop/Cowork、Claude Code、OpenClaw 和本地 Gateway 的可移植模型目录同步及严格别名代理工具。

从已验证的 Windows 个人工作流中提取确定性核心，同时删除个人路径、固定模型数量、端口、应用 ID、UUID、Provider 地址和凭据。它**不宣称**完整模拟 Claude 协议。

## 主要能力

- 从内联/本地 JSON、YAML 或 OpenAI 兼容 `/v1/models` 动态获取模型目录；
- 智能生成 `claude-*` 别名（支持 OpenAI 多模态图像模型、Code Reviewer 与 Google Agents）并阻止冲突和重复；
- 支持在配置文件中声明自定义别名映射规则（`aliasRules` / `transforms`）；
- 分离可见菜单模型与隐藏兼容别名；
- 提供 `inspect`、`plan`、`apply`、`verify`、`rollback`；
- 默认不删除旧模型，只有显式 `--prune` 才会清理；
- 原子写入、备份、事务记录、幂等应用和回滚；
- 严格 Alias Proxy：零停机热重载（`mtime` 自动重载）、默认回环地址、可选本地认证、路径白名单、请求体限制、超时、窄 CORS、健康检查和结构化日志；
- Windows 策略注入器：原生支持 Windows 商店版 MSIX 容器沙箱穿透（`Invoke-CommandInDesktopPackage`）与客户端平滑冷重启；
- 实验性 Linux 用户服务模板、OpenClaw Agent Skill、跨平台 CI 和 Gitleaks。

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

## 平台边界与适配

- Windows：
  - 自动生成 `.reg` 注册表策略文件；
  - 支持普通宿主机注册表导入（`-Apply`）；
  - **原生支持 Windows 商店 MSIX 打包版 Claude Desktop 容器虚拟蜂巢穿透注入（`-PiercingMSIX`）**，彻底杜绝策略无法在容器生效的问题；
  - 支持后台托盘进程自动终止与重新唤醒（`-RestartApp`）。
- macOS：CLI/Proxy 可用；mobileconfig、LaunchAgent 和 MDM 写入仍属实验性/待实现。
- Linux：CLI/Proxy 与 systemd user 模板；不宣称支持 Claude Desktop 下拉菜单。

详见 [references/platforms.md](references/platforms.md)。

## 配置与凭据

JSON 不需要第三方依赖；YAML 需要：

```bash
python -m pip install -e ".[yaml]"
```

远端 Token 只能通过配置中的环境变量**名称**引用，例如 `tokenEnv: MODEL_GATEWAY_TOKEN`。不要把真实值写入配置、命令、日志或仓库。

## 严格代理与热重载

代理仅替换请求体的 `model`、返回可见模型列表并转发 `/v1/messages`；不会修改 Prompt、Tools、Thinking、Metadata 或响应内容。
运行时支持基于清单文件修改时间（`mtime`）的**零停机免重启热加载**。运行前通过受保护环境配置 `CLAUDE_MODEL_SYNC_MANIFEST`、`UPSTREAM_BASE_URL`，并建议配置 `LOCAL_CLIENT_TOKEN`。

## Windows 菜单与策略注入

```powershell
# 仅生成供审查的 .reg 文件
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Output ./generated/claude-models.reg

# 生成、导入宿主并自动穿透 MSIX 容器沙箱
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Apply -PiercingMSIX

# 一键完成策略穿透并重载客户端
./adapters/windows-registry.ps1 -Manifest ./generated/models.json -Apply -PiercingMSIX -RestartApp
```

## 测试

```bash
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q src tests
node --check proxy/server.mjs
node tests/test_proxy.mjs
```

安全政策见 [SECURITY.md](SECURITY.md)，许可证为 MIT。