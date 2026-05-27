# GenSpec Flow Plan For Cache

Date: 2026-05-27

## Purpose

This document records the corrected understanding of the official UCAgent GenSpec workflow and maps it to the current Track1 NutShell Cache workspace.

The key correction is that GenSpec is not just a hand-written specification document. It is a separate UCAgent custom workflow that generates a functional specification before verification work. The workflow should be treated as a staged documentation-generation pipeline, then connected back to the existing verification artifacts.

Official reference:

- https://ucagent.open-verify.cc/content/04_case/00_genspec/

## Official GenSpec Workflow

The official flow has six stages:

| Stage | Name | Main Purpose | Expected Output / Checker |
| --- | --- | --- | --- |
| 1 | `collect_existing_assets` | Scan existing README, design docs, comments, and other available materials; build the first main spec frame. | `{OUT}/{DUT}_spec.md`; `MarkDownHeadChecker` |
| 2 | `augment_with_code` | Walk each source file and enrich the main spec with interface, state-machine, and key-logic details extracted from code. | Updated `{OUT}/{DUT}_spec.md`; `WalkFilesOneByOne` |
| 3 | `complete_subspecs` | Generate finer-grained sub-spec documents for complex submodules. | `{OUT}/{DUT}/*_spec.md`; `BatchMarkDownHeadChecker` |
| 4 | `human_check` | Pause for human review, correction, and missing-design-intent supplementation. | Human confirmation through `HumanChecker` |
| 5 | `functional_specification_analysis` | Extract the FG/FC/CK function and checkpoint label system from the specification. | `{OUT}/unity_test/{DUT}_functions_and_checks.md`; `UnityChipCheckerLabelStructure` |
| 6 | `ref_function_line_map_generation` | Map functional checkpoints to source-code lines for traceability and coverage planning. | `{OUT}/unity_test/{DUT}_line_func_map.md`; `FileLineMapChecker` |

The official output directory defaults to `unity_test`, but the path can be configured through `OUT`.

## Cache Workspace Mapping

Current Cache verification work is already executable and well documented, but it did not start from GenSpec. Therefore GenSpec should be added as a supplemental front-end specification flow without disrupting the working tests.

Current source and documentation inputs:

| Input Class | Cache Workspace Path | GenSpec Use |
| --- | --- | --- |
| Main RTL | `rtl/dut/Cache.v` | Primary source file for Stage 2 code augmentation. |
| Extra RTL / config | `rtl/dut/Test.v`, `rtl/dut/Cache.yaml` | Auxiliary source context. |
| DUT identity and boundary | `docs/dut_selection.md`, `unity_test/Cache_basic_info.md` | Stage 1 existing-asset input. |
| Interface description | `docs/interface_map.md` | Stage 1 seed content; Stage 2 should verify against RTL ports. |
| Verification needs | `unity_test/Cache_verification_needs_and_plan.md` | Stage 1 seed content. |
| Existing FG/FC/CK | `unity_test/Cache_functions_and_checks.md` | Input to Stage 5 comparison; should not be overwritten blindly. |
| Coverage and bug evidence | `docs/coverage_report.md`, `unity_test/Cache_line_coverage_analysis.md`, `unity_test/Cache_bug_analysis.md` | Context for risk and verification-requirement sections. |
| Workflow gap analysis | `docs/workflow_gap_analysis.md` | Tracks which GenSpec deliverables remain missing or completed. |

## Recommended Execution Shape

Use a dedicated GenSpec workspace overlay rather than rewriting the current verification tree in place.

Recommended layout:

```text
genspec_workspace/
├── Cache/
│   ├── Cache.v
│   ├── Test.v
│   ├── Cache.yaml
│   ├── README.md
│   └── docs/
│       ├── dut_selection.md
│       ├── interface_map.md
│       ├── Cache_basic_info.md
│       ├── Cache_verification_needs_and_plan.md
│       ├── Cache_functions_and_checks.md
│       ├── Cache_line_coverage_analysis.md
│       └── Cache_bug_analysis.md
└── genspec_cache.yaml
```

Then run UCAgent with the official GenSpec-style config, for example:

```sh
cd /Users/zzy/Workspace/ucagent/competition/track1_nutshell_cache
ucagent genspec_workspace Cache \
  --config genspec_workspace/genspec_cache.yaml \
  -hm --tui \
  --mcp-server-no-file-tools \
  --no-embed-tools \
  --guid-doc-path /Users/zzy/Workspace/ucagent/examples/GenSpec/SpecDoc/dut_spec_template.md
```

For Codex-backed non-interactive work in this repository, first create a normal UCAgent planning/audit stage to prepare the overlay and document the exact command, then run the GenSpec flow deliberately because Stage 4 requires human review.

## Stage 1-2 Completion Standard

GenSpec Stage 1-2 should be considered complete for this project only when all of the following are true:

- `Cache_spec.md` exists in the selected GenSpec output location.
- The spec includes existing-asset synthesis: DUT boundary, selected RTL source, Picker wrapper, interface map, existing verification goals, and known constraints.
- The spec includes code-derived details from `Cache.v`, not just prose copied from existing docs.
- The RTL-derived section covers:
  - top-level `Cache` ports,
  - CPU request/response ready-valid channels,
  - memory refill and dirty writeback path,
  - MMIO bypass path,
  - coherence probe request/response path,
  - `io_flush` / `io_empty` behavior,
  - `CacheStage1`, `CacheStage2`, and `CacheStage3` responsibilities,
  - Stage3 FSM states for idle, refill, dirty writeback, MMIO, response, and probe/release behavior,
  - meta/data SRAM structure and reset sweep.
- `docs/workflow_gap_analysis.md` is updated from `MISSING` to `PARTIAL` or `PASS` for GenSpec Stages 1-2 with exact artifact paths.
- `top.md` indexes the new GenSpec plan/config/spec artifacts.

## Guardrails

- Do not overwrite `unity_test/Cache_functions_and_checks.md` during early GenSpec work. Treat the existing file as a reviewed verification artifact until Stage 5 is intentionally run.
- Do not modify RTL as part of GenSpec; source files should be read-only inputs.
- Keep generated GenSpec artifacts separate from executable tests so the stable regression flow remains untouched.
- Human review is mandatory before claiming the full six-stage GenSpec flow is complete.

## Immediate Next Step

Run a UCAgent stage that validates this plan, records it as a stage artifact, and updates the workflow index. After that, run the actual GenSpec Stage 1-2 overlay generation as a separate deliberate task.
