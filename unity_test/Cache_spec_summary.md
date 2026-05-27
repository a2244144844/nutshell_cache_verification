# Cache 规格人工审核摘要

本摘要用于人工复核 Cache 主规格与子规格的一致性，覆盖接口、状态机、关键路径、覆盖建议和已知风险。结论只表示当前文档链路下的审核结果，不替代后续人工确认。

审核范围：<ref_file>unity_test/Cache_spec.md</ref_file> 及其可选子规范
<ref_file>unity_test/Cache/CacheStage1_spec.md</ref_file>
<ref_file>unity_test/Cache/CacheStage2_spec.md</ref_file>
<ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>
<ref_file>unity_test/Cache/MetaDataArray_spec.md</ref_file>
<ref_file>unity_test/Cache/DataArray_spec.md</ref_file>
<ref_file>unity_test/Cache/Replacement_spec.md</ref_file>

## 确认通过项

- 主规格与子规格的职责划分一致：`CacheStage1` 负责请求接入与读口拉起，`CacheStage2` 负责命中/替换/forward/MMIO 判定，`CacheStage3` 负责状态机、refill/writeback/MMIO/probe/flush 收尾，`MetaDataArray` 与 `DataArray` 分别承载 metadata 与 data 存储。
  证据见 <ref_file>unity_test/Cache/CacheStage1_spec.md</ref_file>、<ref_file>unity_test/Cache/CacheStage2_spec.md</ref_file>、<ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>、<ref_file>unity_test/Cache/MetaDataArray_spec.md</ref_file>、<ref_file>unity_test/Cache/DataArray_spec.md</ref_file>、<ref_file>unity_test/Cache/Replacement_spec.md</ref_file>。

- 顶层接口覆盖是完整的：CPU 请求/响应、memory refill/writeback、coherence probe、MMIO、flush 与 `io_empty` 均已在主规格中建立端口级描述。
  证据见 <ref_file>unity_test/Cache_spec.md</ref_file>，对应 RTL 入口见 <ref_file>Cache/Cache.v:2057-2107</ref_file>。

- 关键数据通路描述一致：metadata 为 4-way、128-set、21-bit；data 为 4-way、64-bit word 组织；line 内 word 访问与 `addr[5:3]` 相关。
  证据见 <ref_file>unity_test/Cache/MetaDataArray_spec.md</ref_file>、<ref_file>unity_test/Cache/DataArray_spec.md</ref_file>、<ref_file>unity_test/Cache_spec.md</ref_file>。

- 替换策略主线一致：invalid way 优先，其次 LFSR victim；dirty victim 需要先 writeback 再 refill。
  证据见 <ref_file>unity_test/Cache/Replacement_spec.md</ref_file>、<ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>、<ref_file>unity_test/Cache_spec.md</ref_file>。

- 现有规格已经覆盖了主要验证主题：smoke、directed、random、backpressure、MMIO bypass、coherence probe、flush、replacement/eviction、bug evidence。
  证据见 <ref_file>unity_test/Cache_spec.md</ref_file> 与其引用的功能检查资料。

## 待人工复核项

- `io_flush[1]` 的架构语义仍需确认。主规格和 Stage3 规格都表明 `io_flush[0]` 与 `io_flush[1]` 的清空范围不同，但资料同时提示 `io_flush[1]` 在当前 D-cache 场景下可能受断言约束。
  证据见 <ref_file>unity_test/Cache_spec.md</ref_file>、<ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>。

- coherence probe 首次命中时的 `data` 判定口径仍需确认。现有资料更明确的是命中/未命中命令字段，而不是首拍返回 data 的严格稳定性。
  证据见 <ref_file>unity_test/Cache_spec.md</ref_file>、<ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>。

- RTL line coverage 的对外表述需要统一口径。当前资料同时存在“98.4% line coverage”与“当前 active flow 未正式收集 RTL line coverage 报告”的表述。
  证据见 <ref_file>unity_test/Cache_spec.md</ref_file>。

- `Cache.yaml` 的内部寄存器可见性配置更偏向导出/观测约束，其功能意图是否应写入主规格仍需人工确认。
  证据见 <ref_file>unity_test/Cache_spec.md</ref_file>、<ref_file>Cache/Cache.yaml:1-5</ref_file>。

## 未覆盖风险

- Reset sweep 风险：`MetaDataArray` 在复位期间会做 128-set sweep，若测试过早启动，可能把初始化窗口误判为有效读回。
  证据见 <ref_file>unity_test/Cache/MetaDataArray_spec.md</ref_file>、<ref_file>unity_test/Cache_spec.md</ref_file>。

- Dirty victim 回写风险：若 dirty writeback 路径被破坏，可能出现回写缺失并在 refill 前丢失脏数据。
  证据见 <ref_file>unity_test/Cache/Replacement_spec.md</ref_file>、<ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>、<ref_file>unity_test/Cache_spec.md</ref_file>。

- WordIdx 绑定风险：`addr[5:3]` 与线内 word 的对应关系一旦错位，可能导致同一 cache line 内的数据覆盖错误。
  证据见 <ref_file>unity_test/Cache/DataArray_spec.md</ref_file>、<ref_file>unity_test/Cache_spec.md</ref_file>。

- Stage1 回压风险：若 meta/data 读口 ready 在同拍抖动，Stage1 的组合接入口可能产生吞吐下降或请求停顿，协议是否允许这一 stall 需要确认。
  证据见 <ref_file>unity_test/Cache/CacheStage1_spec.md</ref_file>。

- Stage3 与 flush/MMIO 交叠风险：`needFlush`、MMIO 和 burst 状态交互复杂，存在状态提前清零或 stuck 的潜在风险。
  证据见 <ref_file>unity_test/Cache/CacheStage3_spec.md</ref_file>。

## 后续补充建议

- 将 `io_flush[0]`、`io_flush[1]` 的阶段职责写成显式规格条目，并标注当前是否允许在 D-cache 实例中使用 `io_flush[1]`。

- 为 coherence probe 首次命中补一条可执行判定规则，明确 data 字段是否要求稳定、是否依赖前置填充条件。

- 统一主规格中的 coverage 对外口径，建议在最终版中只保留一种表述，并注明其来源文件与适用范围。

- 补充 reset 完成前后的测试前置条件，避免把初始化 sweep 误当成功能行为。

- 若后续要扩展覆盖，建议把 dirty eviction、probe、flush、MMIO bypass、backpressure 单独列成独立检查点，便于与 `Cache.v` 行级追踪映射对齐。

## 结论

当前规格文档已经能够支撑主规格初稿，但 `io_flush[1]`、probe 首次命中 data、coverage 对外口径三项仍属于待人工确认项。
在人工确认前，本摘要仅用于审核记录，不应视为最终闭环规格。
