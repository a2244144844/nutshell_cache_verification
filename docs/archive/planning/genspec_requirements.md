# GenSpec 规范生成 — 输出要求

来源: https://ucagent.open-verify.cc/content/04_case/00_genspec/

## GenSpec 六阶段流程

| Stage | 名称 | 输出 |
|---|---|---|
| 1 | collect_existing_assets | `{OUT}/{DUT}_spec.md` 初始版本 |
| 2 | augment_with_code | 源码增强后的 spec |
| 3 | complete_subspecs | `{OUT}/{DUT}/` 子模块 spec |
| 4 | human_check | 人工审核通过 |
| 5 | functional_specification_analysis | `unity_test/{DUT}_functions_and_checks.md` |
| 6 | ref_function_line_map_generation | `unity_test/{DUT}_line_func_map.md`, `unity_test/{DUT}_line_map_analysis.md` |

## GenSpec 输出目录结构

```
output/
├── {DUT}_spec.md              # 主规范文档
├── {DUT}/                     # 源码目录(只读)
│   ├── *.v / *.sv / *.scala  # RTL 源文件
│   └── ...
├── {DUT}/                     # 子规范目录(可选)
│   ├── submodule1_spec.md    # 子模块规范
│   └── submodule2_spec.md
└── unity_test/                         # 功能标签输出
    ├── {DUT}_functions_and_checks.md   # FG/FC/CK 标签清单
    ├── {DUT}_line_func_map.md          # 行与功能映射文档
    ├── {DUT}_line_map_analysis.md      # 行映射分析报告
    ├── {DUT}_spec_summary.md           # 文档检查摘要
    └── {DUT}_spec.md                   # 主规范文档
```

## 对应本项目的输出目录

```
unity_test/
├── Cache_spec.md                        # ✅ 主规范文档
├── Cache/                               # ✅ 子模块规范目录
│   ├── CacheStage1_spec.md
│   ├── CacheStage2_spec.md
│   ├── CacheStage3_spec.md
│   ├── DataArray_spec.md
│   ├── MetaDataArray_spec.md
│   └── Replacement_spec.md
├── Cache_functions_and_checks.md        # FG/FC/CK 标签清单
├── Cache_line_func_map.md               # 行与功能映射文档
├── Cache_line_map_analysis.md           # 行映射分析报告
├── Cache_spec_summary.md                # 文档检查摘要
├── Cache_basic_info.md                  # 额外：基本信息
├── Cache_bug_analysis.md                # 额外：Bug 分析
├── Cache_line_coverage_analysis.md      # 额外：行覆盖率分析
├── Cache_test_summary.md                # 额外：测试总结
├── Cache_verification_needs_and_plan.md # 额外：验证需求与计划
└── README.md                            # 额外：说明
```

## 各文档应包含的 Stage 11-13 内容

| 文档 | 应反映的 Stage 11-13 内容 |
|---|---|
| `Cache_functions_and_checks.md` | DIR-017~022 测试点对应的功能点/检查点 |
| `Cache_line_func_map.md` | 豁免行与功能点的映射关系 |
| `Cache_line_map_analysis.md` | 行覆盖率 100% 分析、分支覆盖率 100% 分析、豁免分析 |
| `Cache_spec_summary.md` | 最终覆盖率数字、豁免汇总 |
| `Cache_test_summary.md` | Stage 11/12/13 新增测试及结果 |
| `Cache_verification_needs_and_plan.md` | 覆盖率 closure 计划与结果 |
