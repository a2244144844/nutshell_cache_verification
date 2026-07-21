# opencode 连接 UCAgent MCP 指南

本文记录如何在 opencode 中通过 MCP 协议连接 UCAgent，让 opencode 作为
MCP client 调用 UCAgent 的验证工具（`RoleInfo`、`CurrentTips`、`Complete`、
`SetCurrentStageJournal` 等），驱动 NutShell Cache 的分阶段验证工作流。

适用范围：所有支持 MCP-Server 调用的 LLM 客户端（opencode、Claude Code、
Qwen-Code、Cherry Studio、VS Code Copilot 等）。本文以 opencode 为例。

## 1. 前置条件

- 已安装 UCAgent 并准备好 Python 虚拟环境（`.venv`）
- 已安装 opencode，并能正常启动
- 工作目录为 `/Users/zzy/Workspace/ucagent`
- 准备一个可用于 MCP 模式的 DUT workspace（例如 `examples/Adder`）

确认 UCAgent 可用：

```bash
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate
ucagent --version
```

确认 DUT workspace 结构（以 Adder 为例）：

```text
examples/Adder/
├── Adder/
│   ├── __init__.py     # 必须存在，空文件即可
│   └── Adder.v
└── README.md            # 可选
```

如果缺少 `Adder/__init__.py`，UCAgent 会报错退出：

```text
ERROR: File(s) Adder/__init__.py do not exist in workspace
```

补建即可：

```bash
mkdir -p examples/Adder/Adder
touch examples/Adder/Adder/__init__.py
```

## 2. 启动 UCAgent MCP Server

UCAgent 的 MCP server 必须在 opencode 连接之前启动，并保持后台运行。

### 2.1 关键参数说明

| 参数 | 作用 | 必要性 |
|------|------|--------|
| `examples/Adder Adder` | workspace 路径与 DUT 名 | 必填 |
| `--mcp-server` | 启用 MCP server | 必填 |
| `--mcp-server-port 5002` | 指定端口（5000 常被 macOS ControlCenter 占用） | 必填 |
| `--mcp-server-no-file-tools` | 不暴露 UCAgent 文件操作工具（由 client 自己处理文件） | 推荐 |
| `--human` | 进入 human 协同模式，使 init_cmds 中的 `start_mcp_server` 被执行 | **关键** |
| `--loop` | 启动 agent loop，防止进程在 pdb 提示符处立即退出 | **关键** |

> **关键经验**：必须同时加 `--human` 和 `--loop`，并用 `sleep infinity |`
> 保持 stdin 不关闭。否则 UCAgent 要么不执行 `start_mcp_server`，要么在
> pdb 提示符处立即退出，MCP server 无法保持运行。

### 2.2 推荐启动命令

```bash
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate

nohup bash -c 'sleep infinity | ucagent examples/Adder Adder \
  --mcp-server --mcp-server-port 5002 --mcp-server-no-file-tools \
  --human --loop' > /tmp/ucagent_mcp.log 2>&1 &

echo "UCAgent MCP PID: $!"
```

### 2.3 验证 MCP Server 已启动

等待约 10-15 秒后检查端口：

```bash
lsof -nP -iTCP:5002 -sTCP:LISTEN
```

期望输出（出现 Python 进程监听 5002 即成功）：

```text
COMMAND   PID  USER   FD   TYPE  DEVICE  SIZE/OFF NODE NAME
Python   82068 zzy    7u  IPv4  ...     0t0  TCP 127.0.0.1:5002 (LISTEN)
```

查看启动日志确认 MCP 已就绪：

```bash
grep -E "FastMCP|5002|Uvicorn" /tmp/ucagent_mcp.log
```

期望关键行：

```text
create FastMCP server with tools: ['ReadTextFile', 'RoleInfo', 'CurrentTips', ...]
FastMCP server started at 127.0.0.1:5002
Uvicorn running on http://127.0.0.1:5002 (Press CTRL+C to quit)
```

快速测试 MCP 接口是否响应：

```bash
curl -s -X POST http://127.0.0.1:5002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

期望返回 `event: message` 开头的 SSE 流，其中包含 `serverInfo` 字段。

### 2.4 停止 UCAgent MCP Server

```bash
pkill -f "ucagent examples"
# 或按 PID 停止
kill <PID>
```

## 3. 配置 opencode 连接 UCAgent MCP

编辑 opencode 全局配置 `~/.config/opencode/opencode.json`，在顶层添加 `mcp`
字段：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "ucagent": {
      "type": "remote",
      "url": "http://127.0.0.1:5002/mcp",
      "enabled": true
    }
  },
  "model": "glm-5.2"
}
```

> opencode 的 `mcp` 配置支持 `local`（启动子进程）和 `remote`（连接已有
> HTTP 端点）两种类型。UCAgent 已经作为独立服务启动，因此用 `remote`。

## 4. 重启 opencode 并验证

```bash
opencode
```

重启后，opencode 会自动加载新的 MCP 配置。UCAgent 提供的工具会以前缀
`mcp__ucagent__` 出现在工具列表中，主要包括：

| 工具 | 作用 |
|------|------|
| `RoleInfo` | 获取当前 UCAgent 角色信息和基本指导 |
| `CurrentTips` | 获取当前阶段的详细任务指导 |
| `Detail` | 获取 Mission 详情和当前进度 |
| `Status` | 获取 Mission 摘要和阶段状态 |
| `ReadTextFile` | 读取文件（让 UCAgent 知晓你读了哪些文件） |
| `RunTestCases` | 运行测试用例 |
| `Check` | 检查当前阶段是否完成（不推进阶段） |
| `Complete` | 检查并推进到下一阶段 |
| `GoToStage` | 跳转到指定阶段 |
| `Exit` | 退出当前任务 |
| `SetCurrentStageJournal` | 记录当前阶段日志 |
| `AllStageJournal` | 获取所有阶段日志 |
| `StageJournal` | 获取指定阶段日志 |

## 5. 推荐的首条提示词

按 UCAgent 官方文档建议，opencode 启动后输入以下提示词开始验证工作：

```text
请通过工具 `RoleInfo` 获取你的角色信息和基本指导，然后完成任务。
请使用工具 `ReadTextFile` 读取文件。
你需要在当前工作目录进行文件操作，不要超出该目录。
```

随后按 UCAgent 的工作流推进：`CurrentTips` → 执行任务 → `SetCurrentStageJournal`
→ `Complete` →（如需）`Exit`。

## 6. 常见问题

### 6.1 端口 5000 被占用

macOS ControlCenter 默认监听 5000 端口。改用 5002 或其他空闲端口：

```bash
lsof -nP -iTCP:5000 -sTCP:LISTEN   # 确认占用
# 改用 5002
--mcp-server-port 5002
```

### 6.2 UCAgent 启动后立即退出

症状：日志里出现 `UCAgent is exited.`，但没看到 `FastMCP server started`。

原因：缺少 `--human` 或 `--loop`，或 stdin 被关闭导致 pdb 立即返回。

解决：必须同时加 `--human --loop`，并用 `sleep infinity |` 保持 stdin：

```bash
nohup bash -c 'sleep infinity | ucagent examples/Adder Adder \
  --mcp-server --mcp-server-port 5002 --mcp-server-no-file-tools \
  --human --loop' > /tmp/ucagent_mcp.log 2>&1 &
```

### 6.3 `File(s) Adder/__init__.py do not exist`

UCAgent 要求 workspace 下存在 `<DUT>/<DUT>/__init__.py`（即使为空）：

```bash
mkdir -p examples/Adder/Adder
touch examples/Adder/Adder/__init__.py
```

### 6.4 opencode 连接 MCP 失败

确认 UCAgent MCP 仍在运行：

```bash
lsof -nP -iTCP:5002 -sTCP:LISTEN
curl -s http://127.0.0.1:5002/mcp
```

如果 UCAgent 已退出，按第 2 节重启。opencode 配置改完后必须**重启 opencode**
才能生效（配置只在启动时加载一次）。

### 6.5 使用 Codex/Claude 后端而非 opencode

UCAgent 也内置了对 Codex、Claude Code、opencode、Qwen-Code 等后端的适配，
配置文件在 `~/.ucagent/setting.yaml` 的 `backend` 段。若想反过来让 UCAgent
作为主控调用这些 CLI，参考 `instruction.md`（Codex 后端）或
`ucagent/setting.yaml`（其他后端）。

## 7. 参考链接

- UCAgent MCP 集成官方文档：<https://ucagent.open-verify.cc/content/02_usage/00_mcp/>
- UCAgent 仓库：<https://github.com/XS-MLVP/UCAgent>
- opencode 配置 schema：<https://opencode.ai/config.json>
- 本项目 Codex 后端使用记录：`instruction.md`
