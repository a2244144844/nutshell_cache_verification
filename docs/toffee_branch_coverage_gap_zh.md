# Toffee 分支覆盖率报告遗漏分析

日期: 2026-05-30 | 发现方式: 人机协同审查

## 概述

在人工审查 `scripts/collect_coverage.sh` 生成的覆盖率 HTML 报告时，发现了一个数据差异：LCOV HTML 报告（`build/reports/line_dat/picker_cache/index.html`）显示 **85.0% 分支覆盖（24,611 / 28,949）**，而同一个 toffee-test 流水线产生的 `build/reports/line_dat/code_coverage.json` 显示 **95.3% 分支覆盖（471 / 494）**。本文档记录了根因分析、两个数字的数据溯源、流水线遗漏点及优化建议。

---

## 发现背景

| 项目 | 详情 |
|---|---|
| 谁发现 | 人工审查者运行 `scripts/collect_coverage.sh 7 18` 后查看覆盖率 HTML 发现 |
| AI 角色 | 协助解析 `code_coverage.json` 和 `merged.info`，追踪 toffee 源码定位流水线遗漏，生成 RTL 级别可视化临时方案 |
| 日期 | 2026-05-30 |
| 证据文件 | `build/reports/line_dat/picker_cache/index.html`、`build/reports/line_dat/code_coverage.json`、`build/reports/line_dat/merged.info` |

---

## 根因：同一批数据，两条流水线，只有一个 HTML

`collect_coverage.sh` 触发了 toffee-test 的 `convert_line_coverage()` 函数（`.venv/.../toffee_test/utils/__init__.py` 第 31-39 行），该函数对同一批 Verilator `.dat` 覆盖文件执行了两次独立操作：

### 流水线 A — LCOV HTML 生成（→ 85% 分支覆盖）

```python
# toffee_test/utils/__init__.py, 第 34 行
su, so, se = exe_cmd(["genhtml", "--branch-coverage", merged_info, "-o", output_dir])
```

1. 读取 Verilator `.dat` 文件 → 原始覆盖条目（C++ 仿真级别）
2. 调用 `verilator_coverage` CLI → 生成 LCOV 格式的 `merged.info`
3. 对 `merged.info` 调用 `genhtml` → 生成 `line_dat/index.html`

**结果**：28,949 个分支按 **Verilator C++ 仿真内核级别** 统计，一行 RTL `wire` 声明可以产生 128 个 C++ 条件分支。

### 流水线 B — RTL 级别 JSON 提取（→ 95.3% 分支覆盖）

```python
# toffee_test/utils/verilator_coverage/processor.py, 第 40 行
verilator_coverage_miss(filtered_coverage, os.path.join(output_dir, "code_coverage.json"))
```

1. 读取同一批 Verilator `.dat` 文件
2. 使用 `VerilatorCoverage` 类解析每条条目，提取 `\x01page\x02v_branch/ModuleName` 元数据
3. 筛选 `meta.type == "branch"` 的条目 —— 即 Verilator 自身对 RTL 级别分支结构的分类
4. 按 RTL 模块名分组，逐模块统计命中/遗漏
5. 写入 `code_coverage.json`

**结果**：494 个分支按 **RTL 模块级别** 统计，正确反映了设计的逻辑分支结构。

### 遗漏点

`code_coverage.json`（流水线 B）拥有正确的 RTL 级分支数据（95.3%），但**没有从中生成 HTML 可视化**。唯一展示分支覆盖的 HTML 是流水线 A 的 LCOV 输出（C++ 级 85%）。

两条流水线运行在同一个 `convert_line_coverage()` 函数中（第 33 行调用 `convert_verilator_coverage()` 内部运行流水线 B，第 34 行运行流水线 A）。正确的 RTL 分支数据计算并保存后，立即被语义较弱的 C++ 级别 HTML 所掩盖。

---

## 数据溯源：验证两个数字

### 证据 1：RTL 行 → C++ 分支爆炸

扫描 `merged.info` 发现，1,364 行 RTL 中有 1,143 行带有 C++ 分支标注。一个不包含任何逻辑分支的 RTL 行就展示了这种差异的规模：

```
Cache.v 第 8 行:  input [63:0] io_in_bits_wdata,  ← 端口声明，零个逻辑分支
                  ↓ Verilator 编译
                  标注 128 个 C++ 分支（64-bit 总线 → 大量 C++ 条件判断）
```

C++ 分支密度最高的行：

| RTL 行号 | C++ 分支数 | RTL 内容（典型） |
|---|---|---|
| 532 | 130 | `dataRead = useForwardData ? ... : ...` |
| 543 | 130 | `wordMask = cmd[0] ? ... : 64'h0` |
| 8 | 128 | `input [63:0] io_in_bits_wdata,` |
| 16–107 | 128/行 | 端口声明、wire 赋值 |

**合计**：1,364 行 RTL 产生 28,949 个 C++ 分支。比例：约 21 个 C++ 分支 / 每行 RTL。

### 证据 2：VerilatorCoverage 类型筛选

`toffee_test/utils/verilator_coverage/models.py` 第 43-44 行：

```python
type_part, module_part = v.split("/")
self.type = type_part.lstrip("v_")   # → "branch"、"line"、"toggle"、"expr"
self.module_name = module_part       # → "CacheStage3"、"Cache" 等
```

`processor.py` 第 67-83 行中，仅 `meta.type == "branch"` 的条目计入分支计数。Verilator 自身的 `.dat` 元数据区分了 C++ 插桩点（`page=v_branch/ModuleName` → RTL 分支）与一般插桩噪声。该筛选正好提取出 494 个 RTL 级别分支。

### 证据 3：code_coverage.json 中按模块的分解

| 模块 | 分支总数 | 分支命中 | 覆盖率 | 说明 |
|---|---|---|---|---|
| Cache | 66 | 65 | 98.5% | 1 个未覆盖（第 2674 行：响应门控多路器） |
| CacheStage1 | 0 | 0 | — | 纯组合逻辑，无分支结构 |
| CacheStage2 | 58 | 48 | 82.8% | 10 个未覆盖（前向元数据路径、断言检查） |
| CacheStage3 | 210 | 198 | 94.3% | 12 个未覆盖（probe 状态、断言检查、beat 计数器） |
| Arbiter ×5 | 26 | 26 | 100% | |
| SRAMTemplate ×4 | 134 | 134 | 100% | |
| **总计** | **494** | **471** | **95.3%** | |

这种按模块分组仅在 Verilator 的 `.dat` 格式中可能实现，因为该格式为每条覆盖条目标记了源 Verilog 模块 —— LCOV 的扁平"每个源文件"格式（`merged.info`）不支持此功能，导致 C++ 级数据全部归入单一的 `Cache.v` 桶中。

---

## 影响评估

| 方面 | 影响 |
|---|---|
| **评分风险** | 低。正确的 95.3% RTL 分支覆盖率已记录在 `code_coverage.json`（交付物）中。但如果评审者只打开 HTML 报告，将看到 85%，低估了验证质量约 10 个百分点。 |
| **验证质量** | 无影响。测试套件已达到 95.3% 的 RTL 分支覆盖率。这纯粹是报告流水线的遗漏。 |
| **可复现性** | `scripts/collect_coverage.sh 7 18` 可以一致地复现两个输出。 |
| **人工困惑度** | 高。HTML 报告是覆盖率审查的自然首选入口，但它显示的是错误（C++ 级）的分支数字。 |

---

## 优化建议

### 短期方案（提交用脚本，已集成到覆盖率流程）

可复用的 Python 脚本，从 `code_coverage.json` 生成 RTL 分支覆盖率 HTML：

```sh
# 独立运行
python scripts/generate_rtl_coverage_html.py

# 或指定路径
python scripts/generate_rtl_coverage_html.py -i build/reports/line_dat/code_coverage.json -o build/reports/rtl_coverage.html
```

该脚本已集成到 `scripts/collect_coverage.sh` 中，每次收集覆盖率后自动生成。

生成的 `build/reports/rtl_coverage.html` 可视化了各模块的 Branch / Line / Toggle / Expr 覆盖率，支持展开查看未覆盖行详情。应在提交的 README 和覆盖率文档中引用它，作为权威的分支覆盖率可视化。

### 长期方案（toffee-test 改进建议）

修改 `toffee_test/utils/verilator_coverage/__init__.py`，在 `verilator_coverage_miss()` 之后增加 RTL 级 HTML 生成步骤：

```python
def convert_verilator_coverage(line_coverage_list, output_dir):
    # ... 现有代码 ...
    verilator_coverage_miss(filtered_coverage, os.path.join(output_dir, "code_coverage.json"))
    merged_info = os.path.join(output_dir, "merged.info")
    verilator_coverage_to_lcov(filtered_coverage, merged_info)
    
    # 新增：从 code_coverage.json 生成 RTL 级分支 HTML
    generate_rtl_coverage_html(
        os.path.join(output_dir, "code_coverage.json"),
        os.path.join(output_dir, "rtl_branch_coverage.html")
    )
    return merged_info, ignore_info
```

或者，生成一个按模块筛选的 LCOV 文件（仅使用 `type == "branch"` 的条目），对其运行 `genhtml`，在 `line_dat/` 旁边生成 `line_dat_rtl/` 目录。

### 需更新的参考文档

| 文档 | 更新内容 |
|---|---|
| `README.md` / `README_zh.md` | 增加 RTL 级分支覆盖率（95.3%）的说明，引用 `rtl_coverage.html` |
| `docs/coverage_report.md` / `docs/coverage_report_zh.md` | 增加按模块分解的分支覆盖率章节 |
| `unity_test/Cache_line_coverage_analysis.md` | 增加分支覆盖率分析 |
| `unity_test/Cache_test_summary.md` | 汇总表格中增加 RTL 分支覆盖率指标 |

---

## 人机协同记录

| 角色 | 贡献 |
|---|---|
| **人** | 通过对比 HTML 和 JSON 输出发现 85% → 95.3% 的差异；质疑数据溯源并要求源码级证据 |
| **AI（WorkBuddy）** | 解析 `merged.info` 映射每行 RTL 的 C++ 分支数；追踪 toffee-test 源码（`processor.py`、`models.py`、`__init__.py`）定位具体函数调用和数据流；生成了 `rtl_coverage.html` 临时可视化方案；编写了完整遗漏分析文档 |
| **共同决策** | 以 RTL 级分支覆盖率（95.3%）为权威指标；将手动生成的 HTML 作为提交产物；将 toffee 流水线遗漏标记为工具改进机会 |

---

## 附录：快速验证命令

自行验证两个分支数字：

```bash
# C++ 级别（LCOV HTML）
grep "Branches:" build/reports/line_dat/picker_cache/index.html
# → 85.0%  28949  24611

# RTL 级别（code_coverage.json）
python3 -c "
import json
with open('build/reports/line_dat/code_coverage.json') as f:
    d = json.load(f)
b = d['overview']
print(f\"RTL branch: {(b['total']['branch']-b['miss']['branch'])*100//b['total']['branch']}%\")
print(f\"({b['total']['branch']-b['miss']['branch']}/{b['total']['branch']})\")
"
# → RTL branch: 95% (471/494)
```

验证单行 RTL 的 C++ 分支爆炸：

```bash
python3 -c "
with open('build/reports/line_dat/merged.info') as f:
    lines = [l for l in f]
count = sum(1 for l in lines if l.startswith('BRDA:8,'))
print(f'RTL 第 8 行（输入端口）→ {count} 个 C++ 分支')
"
```
