# Verification Instruction
You are working inside the Track1 NutShell Cache verification workspace.
Your role is to make each new verification implementation stage visibly
UCAgent-driven while using Codex as the backend engineering agent.

Work stage by stage. For each stage:
1. Inspect the listed files before editing.
2. Keep changes scoped to that stage.
3. Run the requested test or regression command.
4. Create the requested UCAgent output artifact under docs/ucagent_output.
5. Update docs/test_points.md and docs/ai_collaboration_report.md with
   exact command results.
6. Call SetCurrentStageJournal with files changed, commands run, and
   pass/fail result.
7. Call Complete only after the required output files exist.
8. When a stage is launched with scripts/run_ucagent_stage.sh, call Exit
   immediately after Complete so the run stays on one explicit stage.
