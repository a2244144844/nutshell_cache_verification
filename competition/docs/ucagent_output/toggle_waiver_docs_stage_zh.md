# Stage 18：翻转豁免文档闭环

日期：2026-05-31 | UCAgent 阶段：`toggle_waiver_docs`

## 背景

Stage 17 确认翻转覆盖率平台为 88.4%（24947/28227）后，本阶段将翻转豁免正式化至所有 GenSpec 和项目文档。

## 最终覆盖率

```
Line:   1359/1359 = 100.0%
Branch: 471/471  = 100.0%
Toggle: 24947/28227 = 88.4%  （已豁免：3,280，类别 T-A~T-F）
Expr:   137/137 = 100.0%
37 tests, 0 failures
```

## 豁免机制

翻转豁免采用**文档化方式**——不编码在 `conftest.py` `ignore_patterns` 中。原因：

1. `toffee_test` 的 `filter_coverage()` 不具备类型感知——基于行号的过滤会无差别地影响所有覆盖率类型
2. 添加 195+ 个翻转专用的行范围会屏蔽同一行上未来的行/分支/表达式回归
3. GenSpec 不要求 100% 翻转覆盖率——重点在线、分支和功能覆盖
4. 豁免类别（T-A 至 T-F）已有清晰的结构性理由

## 豁免类别

| 类别 | 描述 | 受影响模块 |
|---|---|---|
| T-A | SRAM 地址/数据总线位 | SRAMTemplate、SRAMTemplateWithArbiter 等 |
| T-B | D-cache 常量信号（硬连线为 0）| CacheStage3、CacheStage2、Cache |
| T-C | LFSR 替换位（需 2^64 周期）| Cache、Arbiter_4 |
| T-D | 仅断言条件信号 | CacheStage2、CacheStage3、Cache |
| T-E | 仅复位/固定信号 | 全部 |
| T-F | 未使用/NC 端口位 | Arbiter 系列 |

## 结论

88.4% 的翻转覆盖率是本 I-cache DUT 的实际最大值。剩余 3,280 次缺失全部属于结构性原因，在 T-A 至 T-F 类别下以文档化方式正式豁免。
