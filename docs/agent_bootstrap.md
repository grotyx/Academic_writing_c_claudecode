# manuwright agent instructions

This paper uses the manuwright manuscript engine. These rules are mandatory for every agent (Claude Code, Codex, Antigravity/Gemini, opencode, Muse).

- Read the rules before work: `manuwright rules` (full workflow) or `manuwright rules <keyword>` (one section).
- Plan first: never write a manuscript section without an approved `drafts/draft_plan.md`, and never write analysis code without an approved `data/analysis_plan.md`. Approved means the author checked `- [x] 사용자 승인 완료`. Never tick it yourself.
- Grounding: cite only `[EVID:id]` entries present in `knowledge/evidence.md`; use only numbers present in `results/*.csv`. Never fabricate references, statistics, approvals or review records.
- Gates: do not move past a phase without a recorded PASS. Verify with `manuwright verify --project project.json --profile draft|revision|submission` and the standalone checks (`manuwright citations|numbers|gate ...`).
- Hooks enforce plan-first only in Claude Code and Codex. In other agents, run `manuwright verify` before claiming a step is done.
