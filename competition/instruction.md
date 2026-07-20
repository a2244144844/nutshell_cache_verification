# UCAgent + Codex 联合使用说明

本文记录当前机器上已经验证通过的 UCAgent + Codex CLI 联合使用方式。

## 1. 已验证链路

已跑通的最小链路如下：

```text
UCAgent workflow
  -> backend.codex
  -> codex exec
  -> UCAgent MCP Server
  -> SetCurrentStageJournal / Complete / Exit
```

验证结果：Codex 通过 UCAgent MCP 工具创建了 `output/smoke.md`，随后调用 `Complete` 完成阶段，再调用 `Exit` 退出任务。

## 2. 基础环境

UCAgent 源码和虚拟环境位置：

```bash
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate
```

检查版本：

```bash
ucagent --version
codex --version
```

## 3. 大模型后端配置

UCAgent 自己调用模型时，读取用户级配置：

```text
~/.ucagent/setting.yaml
```

当前使用 OpenAI-compatible DeepSeek 配置，形态如下：

```yaml
model_type: openai
seed: 42

openai:
  model_name: "deepseek-v4-pro"
  openai_api_key: "<your-api-key>"
  openai_api_base: "https://api.deepseek.com"
  trust_env: false
  reasoning_effort: "high"
  extra_body:
    thinking:
      type: "enabled"
```

`trust_env: false` 用来避免 Python/httpx 读取系统代理导致 TLS 连接异常。

## 4. Codex 后端配置

UCAgent 的 Codex 后端也放在 `~/.ucagent/setting.yaml`：

```yaml
backend:
  codex:
    clss: ucagent.abackend.UCAgentCmdLineBackend
    args:
      cli_cmd_new: "codex exec {UC_ENV_CMD_BACKEND_EX_ARGS} --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox < {MSG_FILE}"
      cli_cmd_ctx: "codex exec {UC_ENV_CMD_BACKEND_EX_ARGS} --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox < {MSG_FILE}"
      pre_bash_cmd:
        - "mkdir -p {CWD}/.codex/"
        - "echo \"\n[mcp_servers.ucagent]\nurl = 'http://127.0.0.1:{PORT}/mcp'\ntool_timeout_sec=600000000000\n\" > {CWD}/.codex/config.toml"
```

这里的 `{PORT}` 会替换为 UCAgent MCP Server 的实际端口。

## 5. 关键启动参数

当前验证通过的关键点是：让 UCAgent 在拉起 Codex 前先启动自己的 MCP Server。

使用这个环境变量：

```bash
export UCAGENT_CMDLINE_START_MCP=1
```

Codex 额外参数用这个环境变量传给 UCAgent 后端：

```bash
export UC_ENV_CMD_BACKEND_EX_ARGS="-m gpt-5.4-mini --ephemeral"
```

可按需改成更强模型，例如：

```bash
export UC_ENV_CMD_BACKEND_EX_ARGS="-m gpt-5.5 --ephemeral"
```

## 6. 推荐运行模板

一般形式：

```bash
UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS="-m gpt-5.4-mini --ephemeral" \
ucagent <workspace> <dut> \
  --config <config.yaml> \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port 5002 \
  --no-embed-tools \
  -s
```

说明：

- `<workspace>`：UCAgent 工作区，里面应有 DUT 目录和输出目录。
- `<dut>`：DUT 名称，例如 `Adder`、`StoreUnit`。
- `--backend codex`：让 UCAgent 调用 Codex CLI。
- `--mcp-server-no-file-tools`：启动 MCP，但不暴露 UCAgent 文件操作工具。Codex 自己有文件系统能力，通常更稳。
- `--exit-on-completion`：全部阶段完成后退出。
- `--mcp-server-port 5002`：避免和本机已有 `5000` 服务冲突。

## 7. Smoke Test 示例

创建最小任务：

```bash
rm -rf /tmp/ucagent_codex_smoke
mkdir -p /tmp/ucagent_codex_smoke/workspace/Smoke
mkdir -p /tmp/ucagent_codex_smoke/workspace/output
```

配置 `/tmp/ucagent_codex_smoke/config.yaml`：

```yaml
mission:
  name: "Codex backend smoke test"
  prompt:
    system: |
      You are running inside a minimal UCAgent smoke test.
      Create the requested Markdown file, then call the UCAgent Complete tool.

template_overwrite:
  OUT: "output"

stage:
  - name: write_smoke_file
    desc: "Write a tiny smoke-test artifact"
    task:
      - "Create output/smoke.md."
      - "The file must contain exactly these two lines:"
      - "# UCAgent Codex Smoke Test"
      - "status: ok"
      - "After the file exists, call Complete to finish this stage."
    output_files:
      - "output/smoke.md"
```

运行：

```bash
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate

UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS="-m gpt-5.4-mini --ephemeral" \
ucagent /tmp/ucagent_codex_smoke/workspace Smoke \
  --config /tmp/ucagent_codex_smoke/config.yaml \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port 5002 \
  --no-embed-tools \
  -s
```

成功后检查：

```bash
cat /tmp/ucagent_codex_smoke/workspace/output/smoke.md
```

期望输出：

```text
# UCAgent Codex Smoke Test
status: ok
```

## 8. 判断是否跑通

日志里应出现类似内容：

```text
FastMCP server started at 127.0.0.1:5002
Processing request of type ListToolsRequest
mcp: ucagent/SetCurrentStageJournal completed
mcp: ucagent/Complete completed
complete: true
mcp: ucagent/Exit completed
```

如果只看到 Codex 启动，但没有 MCP 的 `ListToolsRequest`，说明 Codex 没连上 UCAgent MCP。

## 9. 常见问题

### 5000 端口被占用

本机曾出现 `5000` 被系统服务占用。建议统一用 `5002` 或其他空闲端口：

```bash
lsof -nP -iTCP:5002 -sTCP:LISTEN
```

### Codex 找不到 Complete 工具

通常是 MCP Server 没有在 Codex 启动前起来。确认运行时设置了：

```bash
UCAGENT_CMDLINE_START_MCP=1
```

### Codex 模型请求反复 reconnect

这是 Codex CLI 到模型服务的网络问题，不是 UCAgent MCP 本身的问题。日志里如果后续能 fallback 到 HTTP 并继续执行，通常可以忽略。

### MCP 出现 missing-content-type

如果 `curl http://127.0.0.1:<port>/mcp` 连接不上，说明 UCAgent MCP 没启动。重新检查端口和 `UCAGENT_CMDLINE_START_MCP=1`。

## 10. 用于比赛任务的建议流程

1. 准备赛题给定的 DUT 工作区。
2. 确认 DUT 目录名，例如 `Adder`、`StoreUnit`、`L2TLB`。
3. 使用 `--backend codex` 跑 UCAgent。
4. 让 Codex 通过 MCP 调用 `RoleInfo`、`ReadTextFile`、`SetCurrentStageJournal`、`Complete` 等工具推进阶段。
5. 每完成一个阶段后查看 `unity_test/` 和 `output/` 下的交付文件。
6. 最终检查报告、测试文件、覆盖率文件是否满足赛题要求。

