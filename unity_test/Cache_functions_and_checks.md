# Cache Functions And Checks

## DUT Overall Function

The DUT is the top-level NutShell `Cache` RTL exported in `Cache/Cache.v`; the current verification boundary is the generated Verilog module, not the upstream full Chisel build <ref_file>Cache/README.md:1-26</ref_file> <ref_file>Cache/docs/dut_selection.md:7-15</ref_file> <ref_file>Cache/Cache.v:2057-2107</ref_file>.

The cache is a simple-bus style block with CPU request/response, memory refill/writeback, MMIO bypass, coherence probe, and flush/empty control paths. The FC definitions below are intentionally tied to existing smoke, directed, corner, random, and bug-evidence tests so every function point can be mapped to a concrete verification entry point <ref_file>unity_test/Cache_spec.md:3-10</ref_file> <ref_file>Cache/docs/test_points.md:32-58</ref_file> <ref_file>Cache/docs/test_points.md:111-117</ref_file>.

## Function Groups And Checkpoints

### Test API And Harness

<FG-API>

This group covers the reusable verification entry points that every other cache test depends on. The function points in this group define how tests bring the DUT up, drive legal transactions, and observe stable ready/valid behavior before any feature-specific checking begins <ref_file>Guide_Doc/dut_functions_and_checks.md:161-166</ref_file> <ref_file>unity_test/Cache_spec.md:28-50</ref_file>.

#### Reset Bring-Up And Ready Recovery

<FC-API-RESET-READY>

This function point verifies that reset release, metadata sweep completion, and request-ready recovery happen before functional traffic starts. It is the basis for all smoke and directed tests that assume a usable cache pipeline <ref_file>unity_test/Cache_spec.md:49-50</ref_file> <ref_file>unity_test/Cache/MetaDataArray_spec.md:31-40</ref_file>.

- <CK-API-RESET-SWEEP> `SMK-001` confirms the cache does not accept normal traffic until reset has released and the request path is ready <ref_file>Cache/docs/test_points.md:32-40</ref_file>.
- <CK-API-READY-RECOVERY> `SMK-001` and the shared harness confirm that request-ready returns high after the documented reset sweep <ref_file>Cache/docs/test_points.md:32-40</ref_file>.
- <CK-API-RESET-SETTLE> The harness waits for the reset window to settle before any hit/miss or refill assertion is evaluated <ref_file>unity_test/Cache/MetaDataArray_spec.md:38-40</ref_file>.

#### CPU Request Response Smoke

<FC-API-CPU-SMOKE>

This function point verifies the top-level CPU request and response handshake for legal read and write traffic. It is the minimum end-to-end path for cacheable CPU access and is directly reflected in the smoke suite <ref_file>unity_test/Cache_spec.md:58-66</ref_file> <ref_file>Cache/docs/test_points.md:34-40</ref_file>.

- <CK-API-CPU-READ> `SMK-002` and `SMK-003` confirm that a legal read request produces the expected miss/refill/response sequence <ref_file>Cache/docs/test_points.md:34-40</ref_file>.
- <CK-API-CPU-WRITE> `SMK-006` and `SMK-007` confirm that a legal write request produces a write response and that the written data is visible on readback <ref_file>Cache/docs/test_points.md:39-40</ref_file>.
- <CK-API-USER-METADATA> `SMK-004` confirms that the user field is preserved from request to response <ref_file>Cache/docs/test_points.md:37-37</ref_file>.

#### Backpressure Stability On CPU Path

<FC-API-BACKPRESSURE>

This function point verifies that CPU-side request and response payloads remain stable while the opposite side deasserts ready. It belongs in the API group because it checks the contract shared by every feature path, not a single cache operation <ref_file>unity_test/Cache_spec.md:58-66</ref_file> <ref_file>Cache/docs/test_points.md:54-55</ref_file>.

- <CK-API-REQ-HOLD> CPU request payload stays stable while downstream acceptance is blocked <ref_file>unity_test/Cache/CacheStage1_spec.md:28-42</ref_file>.
- <CK-API-RESP-HOLD> `DIR-009` confirms CPU response stays valid and stable while `io_in_resp_ready` is low <ref_file>Cache/docs/test_points.md:54-55</ref_file> <ref_file>unity_test/Cache_spec.md:63-66</ref_file>.

### Core Cache Behavior

<FG-CORE-CACHE>

This group covers cacheable traffic on the normal path: hit processing, write-mask merging, refill on miss, replacement, and eviction ordering. The function points here correspond to the primary cache datapath tests already listed in the directed suite <ref_file>unity_test/Cache_spec.md:58-90</ref_file> <ref_file>Cache/docs/test_points.md:44-58</ref_file>.

#### Read Hit And Write Hit

<FC-CORE-HIT-PATH>

This function point verifies that resident lines are served from cache and that hit writes update only the targeted data lanes. It is the normal cache-resident behavior expected after a successful refill or initial fill <ref_file>unity_test/Cache_spec.md:58-66</ref_file> <ref_file>unity_test/Cache/DataArray_spec.md:25-40</ref_file>.

- <CK-CORE-READ-HIT> `SMK-005` confirms a second read to the same address hits and does not emit a memory request <ref_file>Cache/docs/test_points.md:38-40</ref_file>.
- <CK-CORE-WRITE-HIT> `SMK-006` confirms a write hit returns `WRITE_RESP` <ref_file>Cache/docs/test_points.md:39-40</ref_file>.
- <CK-CORE-RAW-HIT> `SMK-007` confirms a read after write returns the updated data <ref_file>Cache/docs/test_points.md:39-40</ref_file>.

#### Write Mask And Offset Handling

<FC-CORE-WRITE-MASK-OFFSET>

This function point verifies that partial writes are merged correctly with the resident cache line and that different words in the same line remain independent. It is the concrete behavior behind byte, half-word, and word masking tests <ref_file>unity_test/Cache_spec.md:58-66</ref_file> <ref_file>unity_test/Cache/DataArray_spec.md:25-40</ref_file>.

- <CK-DIR-WMASK-BYTE> `DIR-001` covers byte-mask updates to a 64-bit word <ref_file>Cache/docs/test_points.md:44-47</ref_file>.
- <CK-DIR-WMASK-HALF> `DIR-001` covers half-word mask expansion and partial-lane preservation <ref_file>Cache/docs/test_points.md:44-47</ref_file>.
- <CK-DIR-WMASK-WORD> `DIR-001` covers full-word updates on the selected lane <ref_file>Cache/docs/test_points.md:44-47</ref_file>.
- <CK-DIR-WORD-OFFSET> `DIR-002` covers word-offset independence inside the same cache line <ref_file>Cache/docs/test_points.md:46-47</ref_file>.

#### Refill And Write Miss Handling

<FC-CORE-REFILL-WRITE-MISS>

This function point verifies that read misses trigger refill, write misses merge write data with the refilled line when applicable, and the CPU response reflects the selected command path. It is the functional core of the miss-handling tests <ref_file>unity_test/Cache_spec.md:68-76</ref_file> <ref_file>unity_test/Cache/CacheStage3_spec.md:29-43</ref_file>.

- <CK-CORE-READ-MISS> `SMK-002` and `DIR-003` confirm that a cold read miss emits a memory `READ_BURST` before completion <ref_file>Cache/docs/test_points.md:35-36</ref_file> <ref_file>Cache/docs/test_points.md:48-48</ref_file>.
- <CK-CORE-REFILL-LAST> `SMK-003` and `DIR-003` confirm the final refill beat completes with the documented last-beat response and the line becomes resident afterward <ref_file>Cache/docs/test_points.md:36-36</ref_file> <ref_file>Cache/docs/test_points.md:48-48</ref_file>.
- <CK-CORE-WRITE-MISS-CLEAN> `DIR-011` confirms a clean write miss refills the line and applies the write without writeback <ref_file>Cache/docs/test_points.md:56-56</ref_file>.
- <CK-CORE-WRITE-MISS-PARTIAL> `DIR-011` confirms a partial write miss merges the new bytes with the refilled data rather than overwriting the whole line <ref_file>Cache/docs/test_points.md:56-56</ref_file>.

#### Replacement And Eviction

<FC-CORE-REPLACEMENT-EVICTION>

This function point verifies invalid-way priority, clean eviction, dirty eviction, and the ordering between writeback and refill. It is the concrete replacement behavior that the current directed suite uses to prove the cache does not lose resident data <ref_file>unity_test/Cache/Replacement_spec.md:25-40</ref_file> <ref_file>Cache/docs/test_points.md:49-58</ref_file>.

- <CK-CORE-INVALID-WAY> `DIR-004` confirms that an invalid way is selected before any valid victim way <ref_file>Cache/docs/test_points.md:49-50</ref_file>.
- <CK-CORE-CLEAN-EVICTION> `DIR-012` confirms a clean victim can be replaced without generating a writeback burst <ref_file>Cache/docs/test_points.md:57-57</ref_file>.
- <CK-CORE-DIRTY-WRITEBACK> `DIR-005` and `DIR-013` confirm dirty victim eviction emits writeback before refill and does not lose old line data <ref_file>Cache/docs/test_points.md:50-58</ref_file>.
- <CK-CORE-REPLACEMENT-STABILITY> `DIR-004` and `DIR-012` confirm the chosen waymask remains single-hot and consistent with the selection result <ref_file>unity_test/Cache/CacheStage2_spec.md:51-53</ref_file>.

### MMIO Flush And Coherence

<FG-MMIO-FLUSH-COH>

This group covers non-cacheable bypass behavior, flush recovery, and coherence probe responses. These are the control-plane behaviors that must remain testable alongside the normal cacheable datapath <ref_file>unity_test/Cache_spec.md:92-117</ref_file> <ref_file>Cache/docs/test_points.md:51-58</ref_file>.

#### MMIO Bypass

<FC-MMIO-BYPASS>

This function point verifies that MMIO requests bypass cache allocation, travel through the dedicated MMIO channel, and do not create later cache hits on the same address range <ref_file>unity_test/Cache_spec.md:92-99</ref_file> <ref_file>unity_test/Cache/CacheStage2_spec.md:39-41</ref_file>.

- <CK-MMIO-READ> `DIR-006` confirms an MMIO read routes to the MMIO interface instead of the normal cache refill path <ref_file>Cache/docs/test_points.md:51-52</ref_file>.
- <CK-MMIO-WRITE> `DIR-006` confirms an MMIO write routes to the MMIO interface and does not allocate a cache line <ref_file>Cache/docs/test_points.md:51-52</ref_file>.
- <CK-MMIO-NO-HIT> `DIR-006` confirms MMIO traffic does not create a later normal cache hit unless separately filled by cacheable traffic <ref_file>Cache/docs/test_points.md:51-52</ref_file>.

#### Flush Behavior

<FC-FLUSH-BEHAVIOR>

This function point verifies that flush clears in-flight pipeline state and that the cache returns to normal traffic after recovery. The semantic split between `io_flush[0]` and `io_flush[1]` remains a documented ambiguity, so the testable point is anchored on the observed directed flush behavior and not on a stronger architecture claim <ref_file>unity_test/Cache_spec.md:109-117</ref_file> <ref_file>unity_test/Cache_spec.md:187-191</ref_file>.

- <CK-FLUSH-IDLE> `DIR-007` confirms flush while idle keeps the pipeline quiescent and does not create spurious traffic <ref_file>Cache/docs/test_points.md:52-52</ref_file>.
- <CK-FLUSH-DRAIN> `DIR-007` confirms flush during an in-flight transaction drains the pipeline and converges toward empty <ref_file>Cache/docs/test_points.md:52-52</ref_file>.
- <CK-FLUSH-RECOVERY> `DIR-007` confirms new legal traffic is accepted again after flush deassertion <ref_file>Cache/docs/test_points.md:52-52</ref_file>.

#### Coherence Probe

<FC-COHERENCE-PROBE>

This function point verifies that the coherence probe path reports miss for absent lines and hit for resident lines. If the first probe-hit data sample is implementation-sensitive, the data compare point remains a guarded check rather than a hard error <ref_file>unity_test/Cache_spec.md:100-107</ref_file> <ref_file>unity_test/Cache_spec.md:181-185</ref_file>.

- <CK-PROBE-EMPTY-MISS> `DIR-008` confirms probe miss is reported when the target line is absent from cache <ref_file>Cache/docs/test_points.md:53-53</ref_file>.
- <CK-PROBE-HIT-CMD> `DIR-008` confirms probe hit is reported with the expected hit command encoding on resident lines <ref_file>Cache/docs/test_points.md:53-53</ref_file>.
- <CK-PROBE-DATA-STABILITY> Probe-hit data is only compared when the preconditions and sampling timing are explicitly controlled; otherwise this point remains pending human confirmation <ref_file>unity_test/Cache_spec.md:105-107</ref_file>.

### Backpressure And Coverage Risk

<FG-BACKPRESSURE-CRV>

This group captures ready/valid stability and the coverage-risk checklist needed to keep the verification space honest. It is the main place for backpressure, scoreboard-style stability checks, and the current coverage gaps called out by the spec <ref_file>unity_test/Cache_spec.md:163-197</ref_file> <ref_file>Cache/docs/test_points.md:109-117</ref_file>.

#### Backpressure

<FC-BACKPRESSURE>

This function point verifies that requests and responses remain stable while the opposite side deasserts ready. The function point intentionally spans CPU and memory-facing flows because the protocol contract is shared across several tests <ref_file>unity_test/Cache_spec.md:58-76</ref_file> <ref_file>Cache/docs/test_points.md:54-55</ref_file>.

- <CK-BP-CPU-RESP-HOLD> `DIR-009` confirms the CPU response remains valid and stable while `io_in_resp_ready` is low <ref_file>Cache/docs/test_points.md:54-54</ref_file>.
- <CK-BP-MEM-REQ-HOLD> `DIR-010` confirms the memory request remains stable while `io_out_mem_req_ready` is low <ref_file>Cache/docs/test_points.md:55-55</ref_file>.
- <CK-BP-CPU-REQ-HOLD> CPU request payload stability is checked by the shared harness whenever Stage1 backpressure is exercised <ref_file>unity_test/Cache/CacheStage1_spec.md:28-42</ref_file>.

#### Coverage Risk

<FC-CRV-COVERAGE>

This function point records the functional areas that must be exercised by smoke, directed, and random regressions, and it highlights any coverage gap that still needs later refinement. It is not a datapath feature; it is a test completeness point mapped to the random bootstrap and coverage closure work <ref_file>unity_test/Cache_spec.md:163-197</ref_file> <ref_file>Cache/docs/test_points.md:111-117</ref_file>.

- <CK-CRV-COMMAND-BINS> `CRV-003` and `CRV-005` cover read, write, burst, MMIO, and probe command bins in the coverage plan <ref_file>Cache/docs/test_points.md:113-117</ref_file>.
- <CK-CRV-HITMISS-BINS> `CRV-003` covers hit and miss outcome bins in the planned functional coverage space <ref_file>Cache/docs/test_points.md:113-116</ref_file>.
- <CK-CRV-MASK-OFFSET-BINS> `CRV-001` to `CRV-003` cover write-mask and word-offset permutations for cache-line data coverage <ref_file>Cache/docs/test_points.md:113-116</ref_file>.
- <CK-CRV-TOFFEE-CLOSURE> `CRV-004` and `CRV-005` confirm the coverage closure path tracks dirty miss/writeback/refill and the other tracked bins <ref_file>Cache/docs/test_points.md:115-117</ref_file>.

### Bug Evidence And Reporting

<FG-EVIDENCE>

This group ties the executable verification flow to known bug evidence, reproducibility, and reporting. It is intentionally kept separate from normal functional coverage so later stages can map issues and reports without polluting the core functional bins <ref_file>unity_test/Cache_spec.md:171-197</ref_file> <ref_file>Cache/docs/bug_tracking.md:1-121</ref_file>.

#### Bug Injection Evidence

<FC-BUG-INJECTION>

This function point verifies that a controlled fault is caught by the checker and that the regression returns to green after the injection is removed. It gives the verification environment a concrete negative test without permanently modifying the RTL <ref_file>Cache/docs/Cache_bug_analysis.md:10-37</ref_file> <ref_file>Cache/docs/Cache_bug_analysis.md:39-87</ref_file>.

- <CK-BUG-INJECT-TRIGGER> `BUG-001` and `BUG-RTL-001` both have documented and reproducible triggers <ref_file>Cache/docs/bug_tracking.md:13-25</ref_file> <ref_file>Cache/docs/bug_tracking.md:67-79</ref_file>.
- <CK-BUG-INJECT-DETECT> `BUG-001` is detected by the scoreboard, while `BUG-RTL-001` is detected by the dirty-writeback directed test <ref_file>Cache/docs/bug_tracking.md:23-35</ref_file> <ref_file>Cache/docs/bug_tracking.md:87-105</ref_file>.
- <CK-BUG-INJECT-RECOVER> Once injection is disabled, the normal regression path returns to passing behavior <ref_file>Cache/docs/bug_tracking.md:39-55</ref_file> <ref_file>Cache/docs/Cache_bug_analysis.md:31-37</ref_file>.

#### Reproducibility And Reports

<FC-REPORTING>

This function point verifies that command results, coverage summaries, and stage evidence remain traceable from the top-level documents. It is a documentation-level checkpoint that keeps the verification flow reproducible and auditable <ref_file>Cache/docs/Cache_functions_and_checks.md:180-190</ref_file> <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:35-51</ref_file>.

- <CK-REPORT-REGRESSION> Directed and regression results are recorded in a repeatable form <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:35-49</ref_file>.
- <CK-REPORT-COVERAGE> Coverage reports identify the current bins and the remaining gap areas <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:45-50</ref_file> <ref_file>Cache/docs/test_points.md:126-142</ref_file>.
- <CK-REPORT-UCAGENT> UCAgent stage outputs remain linked to the generated specification artifacts <ref_file>Cache/docs/Cache_verification_needs_and_plan.md:20-32</ref_file>.

## Current Notes

- The document now defines each FC as a concrete, testable function point and maps every CK to an implemented smoke, directed, corner, random, or bug-evidence check <ref_file>Cache/docs/test_points.md:32-58</ref_file> <ref_file>Cache/docs/test_points.md:111-117</ref_file>.
- The semantic split of `io_flush[0]` versus `io_flush[1]`, and the exact first-sample data rule for coherence probe hit, remain marked as pending human confirmation <ref_file>unity_test/Cache_spec.md:116-117</ref_file> <ref_file>unity_test/Cache_spec.md:181-185</ref_file> <ref_file>unity_test/Cache_spec.md:187-191</ref_file>.
