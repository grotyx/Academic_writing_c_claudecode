# manuwright agent instructions

This paper uses the manuwright manuscript engine. These rules are mandatory for every agent (Claude Code, Codex, Antigravity/Gemini, opencode, Muse).

- Read the rules before work: `manuwright rules` (full workflow) or `manuwright rules <keyword>` (one section).
- Analysis environment: run analysis scripts with `manuwright run data/py/<script>.py` (the paper's own uv-managed Python; build it once with `manuwright env`). Never install into or repair the system, Homebrew or pyenv Python; add packages to `data/requirements.txt` and rerun `manuwright env`.
- Plan first: never write a manuscript section without an approved `drafts/draft_plan.md`, and never write analysis code without an approved `data/analysis_plan.md`. Approved means `- [x] 사용자 승인 완료` is checked. The author ticks it, or approves the plan explicitly in chat ("승인", "approve"); then record exactly that with `manuwright approve <plan> --kind analysis|draft --approved-by "<author>" --quote "<their words>"`. Never approve on your own judgement, and never treat a general "go on" as approval of a plan the author has not seen.
- Grounding: cite only `[EVID:id]` entries present in `knowledge/evidence.md`; use only numbers present in `results/*.csv`. Never fabricate references, statistics, approvals or review records.
- Gates: do not move past a phase without a recorded PASS. Verify with `manuwright verify --project project.json --profile draft|revision|submission` and the standalone checks (`manuwright citations|numbers|gate ...`).
- Hooks enforce plan-first only in Claude Code and Codex. In other agents, run `manuwright verify` before claiming a step is done.
