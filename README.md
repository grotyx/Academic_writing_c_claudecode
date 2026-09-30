<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
    <img src="assets/logo.png" width="220" alt="manuwright, the careful senior author">
  </picture>
</p>

<h1 align="center">manuwright</h1>

<p align="center">
  <em>He will not let you cite a paper you have not registered.</em>
</p>

<p align="center">
  <a href="https://github.com/grotyx/Academic_writing_c_claudecode/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/grotyx/Academic_writing_c_claudecode/tests.yml?style=flat-square&color=111111&label=tests" alt="Tests"></a>
  <img src="https://img.shields.io/github/v/tag/grotyx/Academic_writing_c_claudecode?style=flat-square&color=111111&label=release" alt="Release">
  <img src="https://img.shields.io/badge/python-3.10%2B-111111?style=flat-square" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/works%20with-5%20agents-111111?style=flat-square" alt="Works with 5 agents">
  <img src="https://img.shields.io/badge/license-CC%20BY%204.0-111111?style=flat-square" alt="CC BY 4.0">
</p>

<p align="center">
  <strong>Plan first &middot; every citation registered &middot; every number from your data &middot; gates before submission</strong><br>
  <sub>A medical-manuscript workflow for AI agents: Claude Code, Codex, Antigravity, opencode and Muse share one verification engine.</sub>
</p>

<p align="center">
  <sub><a href="README.ko.md">한국어</a> &middot; <a href="README.ja.md">日本語</a> &middot; <a href="README.zh.md">中文</a></sub>
</p>

---

You know him. The senior author in every good lab. Reads the draft with a pen in hand. Circles a sentence and asks, quietly, *"Which paper says that?"* Circles a number: *"Which table?"* Nothing leaves the lab until he signs it.

manuwright puts him inside your AI agent.

## Before / after

You ask your agent to write the Results section before the plan is settled.

Without manuwright, it writes fluent prose, cites a plausible paper that does not exist, and rounds a mean it never read.

With manuwright:

```text
BLOCKED by workflow gate (Rule 8): drafts/draft_plan.md has not been approved.
Create the draft plan first, get author approval, then draft sections.
```

And once the plan is approved, every claim has to survive the checkers:

```text
$ manuwright citations drafts/03_introduction.md
GATE FAIL
citation: EVID:smith_2021
reason: citation id not found in knowledge/evidence.md

$ manuwright numbers drafts/05_results.md
GATE FAIL
number: 54.3
reason: number not found in results CSV files
```

## How it works

```text
 evidence.md   ┐
 results/*.csv ┼──▶ approved plan ──▶ draft ──▶ gates ──▶ QC ×3 ──▶ signed build
 style spec    ┘                                  ├ citations
                          ▲                       ├ numbers
                    hooks block                   └ semantic review (independent)
                    writes without it
```

| Guarantee | Enforced by |
|---|---|
| No section before an approved draft plan; no analysis code before an approved analysis plan | Agent hooks (Claude Code, Codex) and `manuwright verify` |
| Every `[EVID:id]` exists in `knowledge/evidence.md` with a verified source | `manuwright citations` |
| Every reported number exists in `results/*.csv` | `manuwright numbers` and result bindings |
| Reviews go stale when a source, plan or the engine changes | sha256 snapshots in every receipt |
| Submission needs human signoff, AI-use disclosure and a completed checklist | `manuwright verify --profile submission` |

The engine never invents approvals or reviews. It records decisions that humans made.

## Install

Two ways, one engine. Pick one.

**A. Template (no install).** Clone the repository and write inside it. Claude Code picks up `.claude/`; Codex and Gemini read `AGENTS.md` and `GEMINI.md`.

```sh
git clone https://github.com/grotyx/Academic_writing_c_claudecode my-paper
```

**B. Installed engine.** One CLI for all your papers, plus adapters for each agent.

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.8.5
manuwright agents install --dry-run     # preview, then run without --dry-run
manuwright init my-paper
```

| Agent | What `manuwright agents install` adds | Plan-first enforcement |
|---|---|---|
| Claude Code | plugin `manuwright@manuwright`: skills + hooks | hook blocks the write |
| Codex | plugin `manuwright@manuwright`: skills + hooks (trust once) | hook blocks `apply_patch` |
| Antigravity (`agy`) | plugin with skills | `manuwright verify` |
| opencode | skills in `~/.config/opencode/skills` | `manuwright verify` |
| Muse | user skills | `manuwright verify` |

**Update.** `manuwright update` installs the newest release and `manuwright agents update` refreshes the adapters. Opt in to automatic patch updates with `manuwright config set auto-update on`: it checks once a day and never applies an update that would invalidate a paper's current review. Template users: `git pull`, or see the [migration guide](docs/migration_guide.md).

**Uninstall.** `claude plugin uninstall manuwright@manuwright`, `codex plugin remove manuwright@manuwright`, `agy plugin uninstall manuwright`, `muse skills uninstall manuwright`, then `uv tool uninstall manuwright`.

## Commands

| Command | What it does |
|---|---|
| `manuwright init [folder]` | Start a paper folder: manifest, plan templates (unapproved), evidence registry, agent rules |
| `manuwright rules [keyword]` | Print the workflow rules, or one section |
| `manuwright verify --project project.json --profile draft\|revision\|submission` | Run every check for that stage |
| `manuwright citations \| numbers \| abstract \| crossrefs \| lint ...` | Run one checker on one file |
| `manuwright gate` / `verify-all` | Check a phase-gate ledger against live checkers |
| `manuwright search "<query>"` | Search PubMed and print evidence entries |
| `manuwright packet` / `build` | Local review packet / gated DOCX build |
| `manuwright update`, `agents install\|update`, `config` | Releases, agent adapters, auto-update |

In Claude Code the template also ships slash commands: `/verify`, `/search-evidence`, `/import-doi`, `/style-pass`, `/verify-claims`, `/suggest-citation`, `/cite-stance`, `/evidence-table`, `/paper-debate`, `/critical-review`, `/editor-review`.

## The workflow

| Phase | You and the agent | Gate |
|---|---|---|
| 1 Setup | Topic, journal, study design; register references | sources verified in `evidence.md` |
| 2 Analysis | Analysis plan, scripts, results CSV, tables | plan approved before any script |
| 3 Draft plan | Key message, claim-to-citation map, outline | plan approved before any section |
| 4 Draft | Methods, Results, Introduction, Discussion, Conclusion, Abstract | citation, number, logic, constraint checks per section |
| 5 Style | Journal style from your own exemplar | measurable style metrics |
| 6 QC | At least 3 rounds; checklist (CONSORT, STROBE, PRISMA, CARE) | recorded in `review/qc_log.md` |
| 7 Finalize | DOCX manuscript, title page, tables | submission profile PASS + human signoff |
| 8 Revision | Response letter, revised sections | every change claim and every reviewer comment checked |

Full rules: [WORKFLOW.md](WORKFLOW.md). Everything that used to live in this README (features, project structure, document list): [docs/guide/overview.md](docs/guide/overview.md).

## FAQ

**Does it write the paper for me?** It helps an agent draft inside your rules. You decide the message, approve the plans, and sign off. Human and co-author review stay mandatory.

**Does anything leave my machine?** Checks run locally. Sending text to another model (external review, PubMed search) happens only when you run those commands.

**Where do my real manuscripts go?** In a private folder or repository, never in a public clone of this template. `manuwright init` creates one.

**Why "manuwright"?** Manuscript + *wright*, an old word for a maker: playwright, shipwright. Someone who builds manuscripts carefully.

## Documentation

[Harness guide](docs/harness_guide.md) &middot; [Workflow reference](docs/workflow_reference.md) &middot; [Verification protocol](docs/verification_protocol.md) &middot; [Writing guide](docs/writing_guide.md) &middot; [QC guide](docs/qc_guide.md) &middot; [Distribution design](docs/distribution_plan.md) &middot; [Changelog](CHANGELOG.md)

## Author

**Professor Sang-Min Park, M.D., Ph.D.**, Department of Orthopaedic Surgery, Seoul National University Bundang Hospital, Seoul National University College of Medicine. <https://sangmin.me/>

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital. Share and adapt for any purpose with attribution.
