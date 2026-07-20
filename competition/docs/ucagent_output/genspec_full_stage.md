# UCAgent GenSpec Full Stage

Date: 2026-05-27

## Purpose

Record the execution of the official UCAgent GenSpec workflow for the Track1 NutShell Cache DUT. This stage complements the already-implemented verification environment with a specification-first artifact chain: RTL-derived spec, sub-specs, FG/FC/CK matrix, and CK-to-RTL line map.

## Inputs

| Path | Role |
| --- | --- |
| `/Users/zzy/Workspace/ucagent/competition/genspec_cache.yaml` | Root copy of the GenSpec configuration used for this run. |
| `/Users/zzy/Workspace/ucagent/competition/genspec_workspace/genspec_cache.yaml` | Overlay copy used by the live UCAgent command. |
| `/Users/zzy/Workspace/ucagent/competition/genspec_workspace/Cache/Cache.v` | UCAgent-visible DUT RTL copied from the selected Picker Cache RTL. |
| `/Users/zzy/Workspace/ucagent/competition/genspec_workspace/Cache/docs/` | Existing project documents supplied as reference context. |

## Command

```bash
source /Users/zzy/Workspace/ucagent/.venv/bin/activate
UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS='-m gpt-5.4-mini --ephemeral' \
ucagent genspec_workspace Cache \
  --config genspec_workspace/genspec_cache.yaml \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port 5004 \
  --no-embed-tools \
  -s \
  --guid-doc-path /Users/zzy/Workspace/ucagent/examples/GenSpec/SpecDoc/dut_spec_template.md
```

The run reached `human_check` and generated `Cache_spec_summary.md`. Because the interactive human pass could not be injected cleanly under `--exit-on-completion`, the reviewer-approved continuation was resumed explicitly from the next functional-analysis stage:

```bash
source /Users/zzy/Workspace/ucagent/.venv/bin/activate
UCAGENT_CMDLINE_START_MCP=1 \
UC_ENV_CMD_BACKEND_EX_ARGS='-m gpt-5.4-mini --ephemeral' \
ucagent genspec_workspace Cache \
  --config genspec_workspace/genspec_cache.yaml \
  --backend codex \
  --exit-on-completion \
  --mcp-server-no-file-tools \
  --mcp-server-host 127.0.0.1 \
  --mcp-server-port 5004 \
  --no-embed-tools \
  -s \
  --force-stage-index 4 \
  --guid-doc-path /Users/zzy/Workspace/ucagent/examples/GenSpec/SpecDoc/dut_spec_template.md
```

## Stage Results

| GenSpec Stage | Result | Evidence |
| --- | --- | --- |
| collect_existing_assets | PASS | Generated `unity_test/Cache_spec.md`. |
| augment_with_code | PASS | Main spec was enriched by reading `Cache.v` and project docs. |
| complete_subspecs | PASS | Generated six sub-specs under `unity_test/Cache/`. |
| human_check | REVIEWED | Generated `unity_test/Cache_spec_summary.md`; continuation was manually approved and resumed from stage 4. |
| functional_specification_analysis | PASS | `UnityChipCheckerLabelStructure` passed; final matrix has 5 FG groups and 45 CK labels. |
| ref_function_line_map_generation | PASS | `FileLineMapChecker` passed; all `Cache/Cache.v` lines are mapped or ignored. |

## Generated Artifacts

| Path | Purpose |
| --- | --- |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache_spec.md` | RTL-derived main Cache specification. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache/CacheStage1_spec.md` | Stage1 pipeline sub-spec. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache/CacheStage2_spec.md` | Stage2 hit/miss and request-classification sub-spec. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache/CacheStage3_spec.md` | Stage3 refill/writeback/flush/probe sub-spec. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache/MetaDataArray_spec.md` | Metadata SRAM/reset-sweep sub-spec. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache/DataArray_spec.md` | Data SRAM sub-spec. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache/Replacement_spec.md` | Replacement policy sub-spec. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache_spec_summary.md` | Human-review summary produced by the human_check stage. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache_functions_and_checks.md` | GenSpec-aligned FG/FC/CK matrix. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache_line_func_map.md` | CK-to-`Cache.v` line mapping. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/Cache_line_map_analysis.md` | Review notes for the line map. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/tests/Cache_api.py` | Standard API wrapper over existing `CacheEnv`. |
| `/Users/zzy/Workspace/ucagent/competition/unity_test/tests/Cache_function_coverage_def.py` | Standard coverage wrapper over existing `CacheCoverage`. |

## Checker Evidence

- `UnityChipCheckerLabelStructure`: passed in the functional-specification stage.
- `FileLineMapChecker`: passed with `count_pass: 2`, `count_fail: 0`, `count_check: 2`.
- Final message from UCAgent: all stages completed and the mission exited.

## Phase C Validation

| Command | Result |
| --- | --- |
| `source scripts/env.sh && python3 -m py_compile unity_test/tests/Cache_api.py unity_test/tests/Cache_function_coverage_def.py` | PASS |
| `source scripts/env.sh && scripts/run_regression.sh` | PASS — `28 passed in 5.76s` |
| `source scripts/env.sh && scripts/reproduce.sh` | PASS — coverage step `29 passed, 18 warnings in 8.08s`; bug-injection failure was observed as expected; recovery path passed; final `[reproduce] PASS` |

## Human Review Notes

- The generated line map intentionally uses `IGNORE` only for random initialization, generator boilerplate, and non-functional scaffolding.
- The standard API and coverage files are wrappers only; the validated verification behavior still lives in `src/env/cache_env.py` and `src/utils/toffee_coverage.py`.
- Existing regression and reproducibility scripts remain unchanged by this GenSpec closeout.
