# Track1 UCAgent 赛事任务执行步骤

本文根据 `docs/track1_UCAgent_competition_requirements.md` 与 `instruction.md` 梳理，目标是形成一条可执行、可复现、便于评审检查的参赛路线。赛题核心是基于 UCAgent 完成果壳 NutShell Cache 的自动化验证，并证明参赛者完成了从架构理解、验证环境搭建、随机激励、覆盖率闭环到 Bug 追踪的完整硬件验证流程。

## 1. 明确目标与评分重点

### 1.1 最终目标

- 对 NutShell Cache 搭建完整验证环境。
- 使用 Picker 将 RTL 转换为 Python 可驱动的仿真模块。
- 使用 Toffee 组织 Generator、Driver、Monitor、Scoreboard 等验证组件。
- 使用 UCAgent/Codex 辅助理解 RTL、生成原型、定位问题和补全文档。
- 通过人工定制的 CRV、Corner Case、覆盖率模型和故障注入证明验证质量。

### 1.2 高分关注点

- 验证实操深度：基础环境、人工优化、覆盖率闭环，合计 60 分。
- 报告与协同分析：AI 协同记录、工程规范与复现性，合计 40 分。
- 一票否决风险：纯 AI 生成、缺少人工审查、无法运行、无复杂场景、缺少 LICENSE 或工程结构混乱。

## 2. 准备环境与仓库结构

### 2.0 UCAgent 证据原则

本赛题不能只体现“AI 写了代码”，还需要体现 UCAgent 的阶段化操作能力。因此从现在开始，每个关键阶段都应满足两个层次的证据：

- 工程证据：代码、脚本、测试结果、波形、覆盖率和报告真实可复现。
- UCAgent 证据：阶段配置、stage journal、output_files、`Complete` 记录，以及人工复核结论。

如果某个阶段只是由 Codex 直接在工作区完成，而不是由 UCAgent stage 调度，应在 `docs/ai_collaboration_report.md` 中如实标注，不能把 Codex 直接执行包装成 UCAgent 已执行。

### 2.1 准备工作区

1. 准备赛题给定的 NutShell Cache RTL/DUT 工作区。
2. 确认 DUT 目录名，例如 `Cache`、`DCache`、`NutShellCache` 等，后续命令中的 `<dut>` 需要与目录名一致。
3. 确认仓库根目录包含 Apache 2.0 `LICENSE`。
4. 建议建立以下参赛目录：

```text
.
├── LICENSE
├── README.md
├── docs/
│   ├── verification_plan.md
│   ├── coverage_report.md
│   ├── bug_tracking.md
│   └── ai_collaboration_report.md
├── src/
│   ├── env/
│   ├── generator/
│   ├── scoreboard/
│   ├── monitor/
│   └── utils/
├── tests/
│   ├── smoke/
│   ├── random/
│   ├── corner/
│   └── injected_bug/
└── scripts/
    ├── run_smoke.sh
    ├── run_regression.sh
    └── collect_coverage.sh
```

### 2.2 启用本机 UCAgent 环境

```bash
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate
ucagent --version
codex --version
```

### 2.3 确认 UCAgent/Codex 后端配置

检查用户级配置：

```bash
cat ~/.ucagent/setting.yaml
```

重点确认：

- UCAgent 模型后端可用。
- `backend.codex` 已配置。
- `cli_cmd_new` 与 `cli_cmd_ctx` 使用 `codex exec`。
- `pre_bash_cmd` 会写入 `.codex/config.toml` 并连接 UCAgent MCP Server。

### 2.4 推荐启动模板

在实际比赛 DUT 工作区中使用如下模板：

```bash
cd /Users/zzy/Workspace/ucagent
source .venv/bin/activate

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

- `<workspace>`：比赛 DUT 工作区。
- `<dut>`：DUT 目录名。
- `<config.yaml>`：面向本次 Cache 验证任务的 UCAgent stage 配置。
- `UCAGENT_CMDLINE_START_MCP=1`：确保 UCAgent 在 Codex 启动前先拉起 MCP Server。
- `--mcp-server-port 5002`：避开本机常见的 5000 端口占用。

### 2.5 Cache 任务的 UCAgent stage 化要求

在参赛项目中应维护一个 Cache 专用 UCAgent 配置，例如：

```text
competition/track1_nutshell_cache/configs/ucagent_track1_cache.yaml
```

该配置需要把验证任务拆成清晰 stage：

- source inventory and DUT boundary
- Picker export and interface map
- smoke closure
- structured env refactor
- directed tests
- CRV and coverage
- bug injection evidence
- final report package

每个 stage 都必须声明 `output_files`，并在完成前把命令结果、人工修正和下一步风险写入协作报告。

## 3. 阶段一：理解 DUT 并建立最小闭环

### 3.1 RTL 与接口理解

1. 阅读 NutShell Cache 的 RTL、接口文档和上游/下游协议。
2. 使用 UCAgent 辅助总结以下内容：
   - Cache 层级与模块划分。
   - 读写请求接口。
   - miss/hit 判定路径。
   - 替换策略。
   - 脏数据写回流程。
   - 状态机和关键数据通路。
3. 人工复核 UCAgent 输出，避免协议、时序和状态理解错误。

### 3.2 形成基础文档

输出：

- `docs/verification_plan.md`：验证目标、验证范围、核心功能点和风险点。
- `docs/ai_collaboration_report.md`：记录 UCAgent 参与了哪些架构理解工作，人工修正了哪些误解。

### 3.3 使用 Picker 建立可驱动 DUT

1. 编写 Picker 转换配置或构建脚本。
2. 将 Cache RTL 转为 Python 可驱动仿真模块。
3. 编写最小 Python 驱动代码，完成 reset、基础读、基础写。
4. 记录 Picker 构建命令和生成产物位置。

### 3.4 完成 smoke test

输出：

- `tests/smoke/`：最小读写测试。
- `scripts/run_smoke.sh`：一键运行基础测试。
- smoke test 日志或结果摘要。

验收标准：

- DUT 可被 Python/Toffee 驱动。
- reset、基础读、基础写能跑通。
- 结果可复现。

## 4. 阶段二：构建 Toffee 风格验证环境

### 4.1 拆分验证组件

将原型代码重构为结构化组件：

- `src/env/`：顶层验证环境与测试装配。
- `src/generator/`：激励生成器。
- `src/monitor/`：接口监视器和事务采样。
- `src/scoreboard/`：参考模型、结果比较、错误定位。
- `src/utils/`：地址映射、事务类型、日志、公共工具。

### 4.2 建立基础测试集合

至少覆盖：

- 基础读。
- 基础写。
- 写后读。
- cache hit。
- cache miss。
- 替换路径。
- 脏数据写回。

### 4.3 人工 Code Review 与重构记录

在 `docs/ai_collaboration_report.md` 中记录：

- 哪些代码由 UCAgent 生成。
- 哪些地方经过人工重构。
- 人工发现的 AI 输出错误或盲区。
- 修正前后的差异。

验收标准：

- 测试入口明确。
- 组件职责清晰。
- Scoreboard 具备可解释的检查逻辑。
- README 能说明如何运行基础用例。

## 5. 阶段三：强化 CRV、Corner Case 与覆盖率闭环

### 5.1 编写受约束随机激励

重点设计：

- 随机读写混合。
- 地址冲突。
- 连续 miss。
- 同一 set 内替换压力。
- 脏块替换和写回。
- 随机 burst 或连续访问压力。
- 边界地址。
- back-to-back 请求。

### 5.2 补充 Directed Corner Case

针对 UCAgent 难以自动覆盖的场景，人工编写定向测试：

- 固定地址映射到同一 cache set。
- 强制触发替换算法边界。
- 脏数据写回后再次读回校验。
- miss/hit 状态快速切换。
- 特定协议握手延迟或 backpressure。

### 5.3 建立 Functional Coverage

覆盖点建议：

- 事务类型：read/write/flush/refill/writeback。
- hit/miss 类型。
- 替换 way 分布。
- dirty/clean victim。
- 地址 set/tag/offset 分布。
- 连续访问长度。
- 状态机路径。
- Corner Case 命中情况。

### 5.4 覆盖率闭环

1. 运行随机回归。
2. 收集 functional coverage。
3. 分析未覆盖点。
4. 为覆盖率缺口补充 directed test 或调整约束。
5. 目标尽量达到 90% 以上 functional coverage。

输出：

- `tests/random/`：随机测试。
- `tests/corner/`：定向 Corner Case。
- `docs/coverage_report.md`：覆盖率结果、缺口分析、补洞记录。
- `scripts/run_regression.sh`：一键回归。
- `scripts/collect_coverage.sh`：覆盖率收集。

## 6. 阶段四：故障注入与检出能力证明

### 6.1 设计人工 Bug 场景

建议注入或模拟：

- hit/miss 判定错误。
- 替换 way 选择错误。
- dirty bit 更新错误。
- 写回地址拼接错误。
- refill 数据写入错误。
- 特定 backpressure 下响应丢失。

### 6.2 证明验证环境能检出 Bug

每个 Bug 记录：

- Bug 类型。
- 注入位置或模拟方式。
- 触发条件。
- 对应测试用例。
- Monitor/Scoreboard/assertion 如何发现异常。
- 错误日志摘要。
- 修复前后结果对比。

输出：

- `tests/injected_bug/`：故障注入测试。
- `docs/bug_tracking.md`：Bug 追踪、定位、修复与验证记录。

验收标准：

- 至少有若干个可解释的 Bug 检出案例。
- 每个 Bug 都能映射到测试、日志、检查机制和修复说明。

## 7. 阶段五：报告、复现与提交整理

### 7.1 完成验证报告

报告至少包含：

- 项目背景与验证目标。
- NutShell Cache 架构理解。
- 验证计划与覆盖点设计。
- Picker / Toffee / UCAgent 使用方式。
- 验证环境结构说明。
- Generator、Monitor、Scoreboard 设计。
- CRV 策略与 Corner Case 设计。
- 覆盖率结果与缺口分析。
- Bug 注入、发现、定位与修复记录。
- AI 生成内容与人工修正对比表。
- Prompt 策略与协同过程复盘。
- 运行方法与可复现性说明。

### 7.2 完成 README

README 需要明确：

- 环境依赖。
- 构建 Picker 模块的方法。
- smoke test 命令。
- 回归测试命令。
- 覆盖率收集命令。
- 报告文件位置。
- 已知限制。

### 7.3 清理工程

提交前检查：

- 删除无意义中间产物、临时日志和缓存。
- 保留必要的结果摘要、覆盖率报告和 Bug 证据。
- 确认脚本有执行权限。
- 确认所有路径均可复现。

## 8. UCAgent 协同记录建议

建议在每个阶段都写入 `docs/ai_collaboration_report.md`：

| 阶段 | AI 辅助内容 | 人工检查内容 | 发现的问题 | 人工修正 | 证据 |
| --- | --- | --- | --- | --- | --- |
| RTL 理解 | 结构、接口、状态机总结 | 对照 RTL 和协议文档复核 | 记录误解点 | 修正文档 | commit/log |
| 环境原型 | 生成初版 Driver/Monitor | 检查时序和接口握手 | 记录不可运行或不准确处 | 重构组件 | 测试日志 |
| Scoreboard | 生成参考比较逻辑 | 检查一致性模型 | 记录漏检场景 | 增加检查 | failing test |
| CRV | 生成随机测试草稿 | 检查约束有效性 | 记录覆盖率缺口 | 补充约束和 directed test | coverage |
| Bug 注入 | 辅助定位异常 | 人工分析根因 | 记录定位偏差 | 修复并回归 | bug report |

## 9. 最终参赛检查清单

- [ ] 根目录包含 Apache 2.0 `LICENSE`。
- [ ] 仓库结构包含 `src/`、`tests/`、`docs/`、`scripts/`。
- [ ] Picker 构建流程可复现。
- [ ] Toffee 验证环境可运行。
- [ ] `scripts/run_smoke.sh` 可一键运行。
- [ ] `scripts/run_regression.sh` 可一键回归。
- [ ] `scripts/collect_coverage.sh` 可收集覆盖率。
- [ ] 覆盖 Cache 基础读写路径。
- [ ] 覆盖 hit/miss、替换、写回等关键路径。
- [ ] 包含人工编写 CRV。
- [ ] 包含人工编写 Corner Case。
- [ ] Scoreboard 检查逻辑可解释。
- [ ] 包含功能覆盖率模型和覆盖率缺口分析。
- [ ] 目标 functional coverage 尽量达到 90% 以上。
- [ ] 包含故障注入或 Bug 检出证明。
- [ ] 包含 AI 协同过程记录。
- [ ] 明确标注 AI 生成内容和人工修改内容。
- [ ] README 给出环境依赖、运行命令和复现步骤。
- [ ] 删除无意义中间产物和临时文件。

## 10. 推荐执行顺序总览

1. 准备 NutShell Cache DUT 工作区和仓库结构。
2. 配置并验证 UCAgent/Codex 后端。
3. 使用 UCAgent 辅助理解 RTL，人工复核后形成验证计划。
4. 使用 Picker 生成 Python 可驱动 DUT。
5. 使用 Toffee 搭建最小 smoke test 闭环。
6. 拆分 Generator、Driver、Monitor、Scoreboard。
7. 编写基础读写、hit/miss、替换、写回测试。
8. 增加 CRV 和 directed Corner Case。
9. 建立 functional coverage，运行回归并分析覆盖率缺口。
10. 根据缺口补充测试，形成覆盖率闭环。
11. 设计故障注入场景，证明验证环境检出能力。
12. 整理 Bug 追踪、覆盖率报告、AI 协同报告和复现说明。
13. 清理仓库，执行最终一键回归。
14. 提交代码仓库和验证报告。
