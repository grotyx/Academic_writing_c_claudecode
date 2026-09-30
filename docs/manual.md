# manuwright user manual (v1.0.0)

This manual walks through one paper from an empty folder to a verified draft, using the commands and outputs of a real end-to-end run on synthetic trial data (2026-09-30). Rules live in [WORKFLOW.md](../WORKFLOW.md); command details in [harness_guide.md](harness_guide.md). Korean: [manual.ko.md](manual.ko.md).

Screenshots are renders of the agents' terminal text captured during that run (the session had no macOS screen-recording permission), so they show exactly what the tools printed.

## 1. Install and check

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.8.8
manuwright doctor                  # python_supported, hooks.ok, warnings
manuwright agents install --dry-run
manuwright agents install          # Claude Code, Codex, Antigravity, opencode, Muse
```

Restart Claude Code after installing or updating the plugin. The first Codex session in a folder asks you to trust the plugin hooks: choose "Trust all" for the four manuwright hooks. Template users (no install) run the same engine as `python -m harness ...` and `python scripts/<tool>.py ...` inside the cloned repository.

## 2. Start a paper

```sh
manuwright init my-paper
cd my-paper
```

`init` creates `project.json`, `data/analysis_plan.md` and `drafts/draft_plan.md` (templates, not approved), `knowledge/evidence.md`, the agent rule files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) and empty `results/`, `review/`, `output/`. It never overwrites a file and never approves anything. Keep real manuscripts in a private folder, not in a public clone of the template.

Put the data in `data/` (for example `data/raw_data.csv` or `.xlsx`).

## 3. Register evidence

```sh
manuwright search "minimally invasive versus open lumbar fusion randomized" --max 8
manuwright search fetch 31476471 34602458 --format evidence
```

Copy the entries into `knowledge/evidence.md` and fill the summary fields from what you actually read. Mark `Source Status: abstract-only` until you have read the full text. Only IDs registered here can be cited, as `[EVID:miller_2020_pmid31476471]`.

## 4. Analysis plan, approval, analysis

1. Write `data/analysis_plan.md`: research question, population, variables, statistical methods, significance and multiplicity, missing data.
2. The author reads it and ticks `- [x] 사용자 승인 완료`. An agent must never tick it.
3. Record the decision:

```sh
manuwright record-approval data/analysis_plan.md --kind analysis \
  --approved-by "Author name" --decision-reference "Meeting 2026-09-30"
```

Until then, agents cannot create analysis scripts:

![Plan-first gate](images/manual/04_plan_first_gate.png)

4. Write the scripts in `data/py/`, write every number to `results/*.csv`, and render tables from the CSVs (never type numbers into tables). Then check:

```sh
manuwright numbers drafts/table_1.md drafts/table_2.md     # 50 tokens, 0 failures in the demo
```

A wrong value is caught with the closest true value and its location:

![Number check](images/manual/05_numbers_catches_wrong_value.png)

## 5. Draft plan and approval

Fill `drafts/draft_plan.md`: key message, tone, terminology decisions, essential references, evidence gap, claim-to-citation map, table/figure plan, introduction and discussion outlines, limitations, word counts. The author approves it the same way:

```sh
manuwright record-approval drafts/draft_plan.md --kind draft --approved-by "Author name" --decision-reference "..."
```

If the plan chooses a term that the engine registry forbids (the demo used "MIS"), give the paper its own registry: copy the engine's `Style/terminology.md` into the paper's `Style/`, edit the row, and set `"terminology": "Style/terminology.md"` in `project.json`. Both `verify` and the edit-time lint hook then use it.

## 6. Drafting with several agents

Each agent gets one section, the same rules, and the checks to run before it finishes. The prompt used in the demo:

```text
Read AGENTS.md, drafts/draft_plan.md, data/analysis_plan.md, results/*.csv, drafts/table_*.md, knowledge/evidence.md.
Write ONLY drafts/05_results.md. Cite only [EVID:id] from evidence.md. Use only numbers from the results/tables.
The primary endpoint was not significant; never call it a trend. When done run
manuwright numbers drafts/05_results.md and manuwright citations drafts/05_results.md and fix until they pass.
```

| Agent | Section in the demo | What happened |
|---|---|---|
| Codex | Methods | Citation check PASS. Kept the plan's term "MIS" despite the lint warning (fixed in v1.8.6). |
| Antigravity (`agy`) | Results | 41/41 numbers PASS. Asks permission for every file read; approve reads inside the paper folder. |
| Muse | Introduction | Citation check PASS. |
| opencode | Discussion | Citations PASS; 10 number "failures" were literature values, all present in the cited abstracts. |

![Codex writing Methods](images/manual/10_codex_methods.png)

![Antigravity writing Results](images/manual/11_agy_results.png)

![opencode writing Discussion](images/manual/13_opencode_discussion.png)

Discussion and Introduction contain numbers from other papers. Exempt those files from result-number checking with a reason, and let the semantic review check them against the cited evidence (section 7).

Only Claude Code and Codex have hooks that block a write without an approved plan. In Antigravity, opencode and Muse, `manuwright verify` is the gate.

## 7. Verify the draft

`project.json` for the demo (abridged):

```json
{
  "artifacts": ["drafts/01_title.md", "drafts/02_abstract.md", "drafts/03_introduction.md", "drafts/04_methods.md",
                "drafts/05_results.md", "drafts/06_discussion.md", "drafts/07_conclusion.md"],
  "tables": ["drafts/table_1.md", "drafts/table_2.md"],
  "abstract": "drafts/02_abstract.md",
  "numeric_artifacts": ["drafts/02_abstract.md", "drafts/05_results.md", "drafts/table_1.md", "drafts/table_2.md"],
  "numeric_exemptions": {
    "drafts/03_introduction.md": "Literature values; checked against cited evidence in semantic review.",
    "drafts/04_methods.md": "Design parameters (sample size, alpha, follow-up), not results.",
    "drafts/06_discussion.md": "Literature values from cited abstracts plus restated results."
  },
  "terminology": "Style/terminology.md",
  "review_sources": ["results/table1_baseline.csv", "results/table2_outcomes.csv", "results/group_counts.csv"]
}
```

```sh
manuwright verify --project project.json --profile draft
```

![Draft profile PASS](images/manual/20_verify_draft_pass.png)

Lint findings count as failures (en dashes, `p` formatting, too many numbers in the Discussion, forbidden terms). Fix them in the text; do not weaken the registry.

## 8. Independent semantic review

Deterministic checks prove that a number exists in your data and that a citation exists in your registry. They cannot tell whether the sentence means the right thing. For that, build a packet and give it to a different model or a human:

```sh
manuwright packet --project project.json
```

The reviewer writes `review/semantic_review.json` (status, reviewer, `method: independent`, six checks, findings, and the packet's `dependencies` verbatim). In the demo, Codex found 13 problems no checker could see, for example "baseline characteristics were balanced" when baseline ODI was 50.6 vs 46.8, a Tian 2013 citation carrying details its abstract does not contain, and a decompression-only MCID used to judge a fusion trial.

![Round 1 review](images/manual/30_codex_semantic_review.png)

Fix, rebuild the packet, review again. Rule 9 allows two automatic rounds; after that the decision goes to the author. In the demo, round 2 resolved 12 of 13 findings; the remaining one (the allocation mechanism could not be verified from the packet) was escalated.

![Round 2 review](images/manual/31_codex_semantic_review_round2.png)

Any change to a manuscript file, plan, CSV or the engine makes an existing review stale; rebuild the packet and review again.

## 9. Submission

```sh
manuwright verify --project project.json --profile submission
```

![Submission profile BLOCKED](images/manual/21_verify_submission_blocked.png)

Submission additionally needs:

- `result_bindings`: every number in the numeric artifacts bound to a CSV cell with its outcome, group, time point and unit.
- `semantic_review` with status PASS and no open findings.
- `human_signoff`: a real person's decision, with a reference.
- `ai_usage`: which AI tools did what, reviewed by a person.
- `checklist`: the reporting checklist (CONSORT, STROBE, PRISMA, CARE) with item locations.

In the demo these took most of the effort:

- **Bindings.** 155 numbers were bound. Most matched exactly one CSV cell; the rest (for example several `120`s, `60`s and `p < 0.001`s) were assigned by reading each sentence. Keep an explicit override table keyed by file, line, number and occurrence (not by token index, which shifts when a sentence changes), and audit the automatic matches too: a unique value can still carry the wrong label. Add summary rows (for example an "All" row with n = 120) to the results instead of binding a total to an unrelated cell.
- **Checklist.** Download the current official checklist (CONSORT 2025 from the CONSORT-SPIRIT website in the demo), map every item to a location or a reason, and let the independent reviewer check it. The reviewer rejected item 26 twice until group summaries, a risk difference and a risk ratio with CIs were reported. Each new analysis needed an approved analysis-plan amendment and was labelled post hoc.
- **Review rounds.** Seven rounds in total; the last two were clean. Beyond the two automatic rounds of Rule 9, continue only with the author's decision.

![Round 6 review: all six dimensions PASS](images/manual/32_codex_semantic_review_round6_pass.png)

Any later edit makes the review and the signoff stale, as intended. In the demo, fixing reference punctuation after signoff did exactly that; the review and signoff were redone.

![Reviews go stale after a change](images/manual/22_stale_after_edit.png)

Then `manuwright build --project project.json` writes the DOCX package (manuscript, title page, one file per table, `verification.json`, output hashes). It re-checks everything first and refuses stale inputs. Open the files and check them by eye before submitting.

![Submission PASS and build](images/manual/23_submission_pass_build.png)

## 9a. Obsidian library and multi-model review

**Obsidian (optional, recommended).** If you use the Obsidian plugin "Academic Paper Citation Manager", connect it once and every agent can search your reference library over MCP:

```sh
manuwright obsidian status
manuwright obsidian connect            # asks first; --dry-run shows the commands
manuwright evidence import-obsidian kirtley1985influence
```

In the demo, Codex, Muse and opencode called the library through MCP (22,622 indexed chunks); Claude Code was already connected; Antigravity needs its first MCP call in an interactive session. Imported entries keep the citekey as `[EVID:id]` and start as `abstract-only`.

**Reviewers.** Choose any mix of reviewers and models; the writing model is set once so a reviewer using the same model is flagged as not independent:

```sh
manuwright config set main-model claude-opus-5-5
manuwright config set review.reviewers codex,opencode,muse,agy,openrouter
manuwright config set review.opencode-model opencode-go/kimi-k3
manuwright config set review.openrouter-models deepseek/deepseek-v4-pro,qwen/qwen3.7-max
manuwright critical-review --target drafts/05_results.md --out review/critical
```

In the demo, eight reviewers (Codex, opencode with kimi-k3, Muse, Antigravity and four OpenRouter models) each returned a full review. Sending text to OpenRouter models leaves your machine: get the author's consent first.

## 10. Updates

```sh
manuwright update --check
manuwright update && manuwright agents update
manuwright config set auto-update on      # patch releases only, at most daily
```

Auto-update waits when a registered paper pins the engine (`"engine": ">=1.8,<1.9"` in `project.json`) or holds a fresh review that an engine change would invalidate. Roll back with `manuwright update --to <version>`.

## 11. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| A section was written without an approved plan | Hooks only exist in Claude Code and Codex. Template: upgrade to v1.8.5+ (relative hook paths failed after a `cd`). Codex: trust the plugin hooks. Others: run `manuwright verify`. |
| `Hooks need review` in Codex | New or changed plugin hooks. Review, then trust the manuwright hooks. |
| Lint flags a term your plan chose | Give the paper its own `Style/terminology.md` and set `terminology` in `project.json`. |
| `one or more declared artifacts are missing: ...` | `project.json` lists sections that do not exist yet. Edit `artifacts`. |
| Numbers in Discussion fail | Literature values: add a `numeric_exemptions` reason and have the semantic review check them. |
| Review became stale | Something in its dependencies changed. Rebuild the packet and review again. |
| Plugin/CLI version warning | Run `manuwright agents update`, then restart the agent. |
