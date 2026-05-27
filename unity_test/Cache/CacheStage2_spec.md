# CacheStage2 规格说明文档

> 本文描述 `CacheStage2` 的职责：在读出 meta/data 后完成命中判定、替换候选选择、forward 覆盖和 MMIO 位判断。结构说明参考主规格 [Cache 规格说明文档](/Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache/genspec_workspace/unity_test/Cache_spec.md)。

## 简介
- **设计背景**：`CacheStage2` 是请求进入 Stage3 前的组合判定层，负责把 SRAM 读出的所有 way 信息汇总成可执行结果 <ref_file>Cache/Cache.v:55-341</ref_file>。
- **设计目标**：输出单一 `hit/waymask/mmio/forwardData` 结果，使 Stage3 只需处理状态机和外部接口 <ref_file>Cache/Cache.v:128-220</ref_file>。

## 术语与缩写
| 缩写 | 全称 | 说明 |
| ---- | ---- | ---- |
| Stage2 | CacheStage2 | Cache 中段判定层 <ref_file>Cache/Cache.v:55-341</ref_file> |
| hitVec | Hit vector | 四路命中向量 <ref_file>Cache/Cache.v:156-160</ref_file> |
| victimWaymask | Victim way mask | 替换候选 way <ref_file>Cache/Cache.v:161-176</ref_file> |

## RTL源文件
- <ref_file>Cache/Cache.v</ref_file> `CacheStage2` 定义 <ref_file>Cache/Cache.v:55-341</ref_file>。

## 顶层接口概览
| 信号名 | 方向 | 位宽/类型 | 描述 |
| ------ | ---- | -------- | ---- |
| `io_in_valid` / `io_in_ready` | input / output | 1 | 请求握手 <ref_file>Cache/Cache.v:55-117</ref_file> |
| `io_in_bits_*` | input | req + meta/data 读回值 | Stage1 传入的请求与读口结果 <ref_file>Cache/Cache.v:60-116</ref_file> |
| `io_out_bits_hit` | output | 1 | 命中标志 <ref_file>Cache/Cache.v:156-160</ref_file> |
| `io_out_bits_waymask` | output | 4 | 目标 way 选择 <ref_file>Cache/Cache.v:165-176</ref_file> |
| `io_out_bits_mmio` | output | 1 | MMIO 判定结果 <ref_file>Cache/Cache.v:182-186</ref_file> |
| `io_out_bits_forwardData_*` | output | 64 / 4 | forward 覆盖数据 <ref_file>Cache/Cache.v:186-220</ref_file> |

## 功能描述
### 命中与替换
- `hitVec` 由四个 way 的 tag/valid 结果组合得到，任何 way 命中都会令 `io_out_bits_hit` 为真 <ref_file>Cache/Cache.v:156-160</ref_file> <ref_file>Cache/Cache.v:214-215</ref_file>。
- `invalidVec` 先于 LFSR victim 被检查；只要存在 invalid way，就优先选择 invalid way <ref_file>Cache/Cache.v:166-176</ref_file>。
- `victimWaymask` 由 LFSR 低两位决定，属于回退选择路径 <ref_file>Cache/Cache.v:161-165</ref_file>。

### Forward 逻辑
- `isForwardMeta` 与 `isForwardData` 在同拍写回时覆盖读值，避免读取旧 meta/data <ref_file>Cache/Cache.v:131-142</ref_file> <ref_file>Cache/Cache.v:187-220</ref_file>。
- Stage2 使用寄存器保存 forward 信息，确保跨拍一致性 <ref_file>Cache/Cache.v:132-142</ref_file> <ref_file>Cache/Cache.v:189-220</ref_file>。

### MMIO 判定
- `io_out_bits_mmio` 由地址命中 0x3000_0000 / 0x4000_0000 区间推导 <ref_file>Cache/Cache.v:182-186</ref_file> <ref_file>Cache/Cache.v:216-216</ref_file>。
- 该信号只决定后续走 MMIO 路径，不在 Stage2 中发起外部请求 <ref_file>Cache/Cache.v:182-186</ref_file>。

### 写掩码处理
- Byte mask 被展开为 64-bit `wordMask`，用于 Stage3 的写数据合并 <ref_file>Cache/Cache.v:533-543</ref_file>。
- `hitWrite` 仅在命中且写请求时成立；这直接影响 data/meta 写回路径 <ref_file>Cache/Cache.v:551-556</ref_file>。

## 状态机与时序
- `CacheStage2` 没有显式外部状态枚举，但内部保存 forward/waymask/victim 相关寄存器 <ref_file>Cache/Cache.v:132-142</ref_file> <ref_file>Cache/Cache.v:189-220</ref_file>。
- 由于它是组合判定加少量寄存器的层，验证上应重点看同拍覆盖与下一拍保持性 <ref_file>Cache/Cache.v:221-281</ref_file>。

## 验证需求与覆盖建议
- 需要覆盖 invalid way 优先、四路命中、forward 覆盖、MMIO 地址判定和写掩码展开 <ref_file>Cache/Cache.v:148-176</ref_file> <ref_file>Cache/Cache.v:182-220</ref_file> <ref_file>Cache/Cache.v:533-556</ref_file>。
- 建议对单热 `waymask` 做断言检查，避免多热非法情况进入 Stage3 <ref_file>Cache/Cache.v:262-275</ref_file>。

## 潜在 bug 分析
- **victim 选择回退不确定性（待确认）**：invalid way 优先规则明确，但 victim 由 LFSR 低位决定，若复位或随机初始化策略变化，可能导致替换路径不可重复 <ref_file>Cache/Cache.v:161-176</ref_file>。
