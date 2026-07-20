# DIR-014 / DIR-015 / DIR-016 实现指南

日期：2026-05-28

对应主文档：`docs/dir_014_015_016_guide.md`

## 说明

原文件本身已经是中文实现指南，本文件作为中文镜像入口保留，便于 `top_zh.md` 和中英文对应检查统一索引。

## 目标

通过 UCAgent MCP/Claude Code 执行 DIR-014、DIR-015、DIR-016，闭合 `Cache.v` 剩余 H/I/J 类行覆盖缺口。

## 三个测试点

| 编号 | 场景 | 目标 |
| --- | --- | --- |
| DIR-014 | Probe hit full release | 覆盖 probe hit 后完整 release 序列 |
| DIR-015 | Read-burst hit | 覆盖 READ_BURST 命中路径 |
| DIR-016 | needFlush de-assertion | 覆盖 flush 后 `needFlush` 清除路径 |

## 当前状态

这些实现已经在 line coverage closure 阶段完成，最终 RTL 行覆盖率达到 `1359/1364 (99.6%)`。
