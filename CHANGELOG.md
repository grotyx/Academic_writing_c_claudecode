# Changelog

### v1.8.25 (261003)

- `manuwright setup`: the OpenRouter key can come from the clipboard. In Windows Terminal running PowerShell, pasted text never reached the hidden key prompt, even after v1.8.24. Copy the key and press Enter on the empty prompt: setup offers the key it finds on the clipboard (shown masked, only if it looks like an OpenRouter key, Y/n) before checking and saving it. On macOS the clipboard is read with pbpaste.

### v1.8.24 (261003)

- `manuwright setup`: the main model is a numbered list on Windows (and any terminal without the arrow-key menu) instead of a blank text prompt. Both the list and the arrow menu mark which agent CLI runs each model ("Claude Code installed", "Codex not installed") and put the models you can run first; a model id can still be typed. Typing an agent name such as `claude` is refused with a hint, because it is not a model id and would never flag a reviewer on the same model. The agent-reviewer prompt lists each agent with its install status.
- `manuwright setup`: pasting the OpenRouter key with Ctrl+V in a classic PowerShell window showed nothing, because the console sends Ctrl+V to the program as a control character, not the pasted text. The hidden key prompt now reads the Windows clipboard on Ctrl+V, and arrow/function keys no longer leak into the key.

### v1.8.23 (261003)

- Windows: `manuwright agents update` (and the Obsidian connect step, agent probes and `opencode models`) run agent CLIs by their full PATH location. npm-installed CLIs such as `muse` are `.cmd` shims that `shutil.which` finds but Windows' CreateProcess does not, so a bare name crashed with `FileNotFoundError: [WinError 2]`. A program that still cannot start is reported for that agent and the remaining agents continue.

### v1.8.22 (261003)

- `manuwright agents update` re-adds the Claude and Codex marketplaces from the current engine folder instead of refreshing the registered path. A reinstall that picked another Python (`python3.11` → `python3.12` site-packages) left them pointing at a deleted folder (`ENOENT` in Claude, `marketplace root does not contain a supported manifest` in Codex). Codex's `marketplace upgrade` only refreshes Git marketplaces, so it never updated the local one.
- Manual: how to check an update worked (`manuwright --version`, `update --check`, `claude|codex plugin marketplace list`).

### v1.8.21 (261002)

- Windows (uv install): `manuwright update` no longer runs `uv tool install --force` from inside the running `manuwright.exe`, which Windows cannot replace; the failed reinstall left a half-removed install (`ModuleNotFoundError: No module named 'manuwright'`). It now prints the command to run in a new terminal after closing agent sessions; the same command repairs a broken install.
- `manuwright update` with no newer release says "up to date" instead of reinstalling the current version (`--to` still reinstalls on request).

### v1.8.20 (261002)

- Windows (non-UTF-8 code page, e.g. cp949 on Korean Windows): `manuwright setup` no longer prints a `UnicodeDecodeError` traceback from a background thread while checking the Obsidian library connection. Output of agent CLIs (`claude`/`codex`/`agy mcp`, `opencode models`), `git ls-remote`, `uv pip freeze` and the `doctor` hook probe is now read as UTF-8 (undecodable bytes replaced) instead of the system code page.

### v1.8.19 (261001)

- `manuwright init --refresh-rules` (inside an existing paper) updates only its agent rule files (AGENTS.md, CLAUDE.md, GEMINI.md) to the installed engine, keeping `.bak` copies; `manuwright update` points to it. Template checkouts are left to `git pull`.

### v1.8.18 (261001)

- Supplementary material: a new `supplements` list in `project.json` (e.g. `drafts/supp_table_1.md`) is checked like tables and built as separate `supplementary_<name>` files. A `supp…` file listed under `tables` is refused, and two files with the same main table number are refused, because either would overwrite main Table N in the package.

### v1.8.17 (261001)

- `manuwright verify` (and status, packet, build) uses the project.json of the paper folder you are in; `--project` is only needed elsewhere.

### v1.8.16 (261001)

- Chat approval: when the author approves a plan in chat ("승인"), the agent records it with `manuwright approve <plan> --kind analysis|draft --approved-by NAME --quote "..."`; the box is ticked with who/when/what and a hashed receipt is written, so the plan-first hook lets the work continue. Agents still never approve on their own.
- Per-paper analysis environment: `manuwright env` builds a uv-managed Python 3.12 with `data/requirements.txt` (pandas, numpy, scipy, statsmodels, matplotlib, openpyxl) outside the paper folder and writes `data/environment.lock.txt`; `manuwright run <script>` runs analysis scripts with it. A broken system, Homebrew or pyenv Python no longer blocks analysis.
- OpenRouter key entry in `manuwright setup` shows one `*` per typed or pasted character (Backspace works) and then confirms the key as `sk-or-v1...abcd (N characters)` before checking it.

### v1.8.15 (261001)

- Personal library (`manuwright library`, `~/.manuwright/library/`): named Word styles and Word templates saved for a target journal, the team or yourself (the journal's style is suggested in `manuwright target`) (a .docx designed in Word becomes the base of the built manuscript via `docx.reference`), a team profile copied to each new paper, and a writing style (own/landmark/target-journal anchors, terminology, style spec) copied into each new paper's `Style/`. Style extraction and profile filling are agent tasks in the manuwright skill.
- Word style and reference format are per paper: new `manuwright target` (inside a paper folder) picks the target journal and that paper's Word style from menus and saves them in its `project.json`; `manuwright setup` no longer asks about Word style. `manuwright init` points to it.
- `manuwright setup` asks for the OpenRouter API key when OpenRouter reviewers are chosen (hidden input, checked with OpenRouter, saved owner-only in `~/.manuwright/secrets.json`, never in config.json); `critical_review.py` uses it when `OPENROUTER_API_KEY` is not set.
- Hardening after review: `--replace` stages a new Word template before touching the stored one; templates are checked to be real .docx files; a template's own line/page numbering is never duplicated; `docx.reference` must stay inside the paper and `build.json` stores it relative; Enter in `target` never switches the Word style by itself; the OpenRouter key is written owner-only via an atomic replace; `doctor` reports a saved key; `writing import` skips the engine's guide and example files.

### v1.8.14 (261001)

- `manuwright setup` says how each reviewer is paid: agent reviewers are labelled "Claude Code (subscription)", "Codex (subscription)", "Muse Code (subscription)", "Antigravity / Gemini (subscription)"; OpenRouter menus say "pay per use", opencode menus "opencode Go subscription". A one-line note explains what reviewers do and that the main model is the writer.

### v1.8.13 (261001)

- `manuwright setup` picks models from menus instead of typed ids: the main model from a list, and agent reviewers, OpenRouter and opencode models from arrow-key checklists (Space ticks, a number key fills a recommended set, Esc keeps the current choice). Numbered fallback without a POSIX terminal. The "not independent" check now matches `claude-opus-5-5` and `anthropic/claude-opus-5.5` as the same model.

### v1.8.12 (261001)

- Recommended reviewer models: `manuwright setup` offers numbered sets for OpenRouter (balanced, budget, strong) and opencode (Go, Go budget) with the newest GLM, Kimi, MiniMax, DeepSeek, Qwen, Xiaomi MiMo and Meituan LongCat models, checked against the live lists with an estimated cost per review; typed ids get a "did you mean" suggestion. `manuwright models` prints the sets. The default OpenRouter pool is now the balanced set. Free and contributor tiers are excluded (they may keep prompts).

### v1.8.11 (261001)

- Obsidian connect no longer freezes the terminal: the agent status checks (`codex`/`claude`/`agy mcp …`) run detached from the terminal, so an agent CLI can no longer leave it in raw mode where Enter does nothing; prompts restore the terminal first and treat Ctrl-C/Ctrl-D as "no".

### v1.8.10 (260930)

- Journal reference styles: `"journal"` in `project.json` (or `format-references --journal`) renders the bibliography and in-text markers for 14 presets — ICMJE/Vancouver, AMA (JAMA), NEJM, Lancet, Spine, The Spine Journal, BJJ, JBJS, Neurospine, J Neurosurg Spine, Global Spine J, CORR, Asian Spine J, Eur Spine J — with author cutoffs, page/issue/month/DOI forms, alphabetical order for CORR, grouped markers (`[1–3]`, superscript in Word). `--fetch` caches full PubMed metadata so journals that list every author get them.
- `manuwright setup` exits cleanly on Ctrl-C/Ctrl-D (nothing saved) and asks for OpenRouter models only when a bare `openrouter` reviewer is chosen.

### v1.8.9 (260930)

One batch release:

- `manuwright setup`: one interactive pass over the main model, reviewers and their models, the Word style, auto-update and the Obsidian library.
- DOCX style is configurable: save your default with `manuwright config set docx.<key> <value>` (font, size, heading/subheading size, line spacing, margins, line numbers continuous/page/off, page numbers center/right/off); a `"docx"` block in `project.json` overrides it for one paper (its target journal). The resolved style is recorded in `build.json`. Without either, the output is unchanged.
- `manuwright obsidian install`: installs the Obsidian plugin from its latest GitHub release into a chosen vault (asks first; enables it; optional MCP access; never overwrites). `agents install` offers it when the plugin is missing.
- Obsidian integration marked optional (recommended); without the plugin, `agents install` prints a one-line suggestion.
- CI fixes after v1.8.8: reviewer settings tolerate an environment without a home directory; a test compared a POSIX path string on Windows.

### v1.8.8 (260930)

One batch release (per the author's request, fixes are grouped instead of bumping per fix):

- **Any reviewer, any model.** `critical_review.py --reviewers agent[:model]` accepts `openrouter:<id>`, `claude`, `codex`, `opencode`, `muse` and `agy`, each with an optional model. Local CLIs run in an empty temporary folder in read-only/plan modes and are asked for a text-only answer (Antigravity otherwise tried a shell tool, was auto-denied in headless mode and returned nothing). Tested on the demo manuscript: Codex, opencode (kimi-k3), Muse, Antigravity and four OpenRouter models all returned full reviews.
- **Settings.** `manuwright config set main-model|review.reviewers|review.openrouter-models|review.<agent>-model ...` (and `unset`). Reviews default to these settings; a reviewer that uses the main writing model is flagged `not_independent`.
- **Obsidian integration.** `manuwright obsidian status|connect` registers the "Academic Paper Citation Manager" MCP server (`rag-obsidian`) for Claude Code, Codex, opencode, Antigravity and Muse (asks first, skips connected agents, backs up edited JSON). `manuwright agents install` offers it when the plugin is found. `manuwright evidence import-obsidian <citekey>` turns a vault note (CSL fields and AI summary) into an `abstract-only` evidence entry. Verified on this machine: Codex, Muse and opencode called the library over MCP; Claude Code was already connected; Antigravity needs its first MCP call interactively.
- Manual: submission stage (bindings, checklist, review rounds, stale reviews, build), Obsidian and reviewer sections.
- 414 tests pass.

### v1.8.7 (260930)

- **Reference strings from PubMed imports**: `search_pubmed.py` wrote "et al.." and no period between title and journal ("...: A meta-analysis J Back Musculoskelet Rehabil"), which then appeared in every built reference list. Fixed, with a test; the old test had encoded the double period. Found while visually checking the first fully built DOCX package of the synthetic demo paper.

### v1.8.6 (260930)

Second end-to-end run: four agents drafted sections (Codex Methods, Antigravity Results, Muse Introduction, opencode Discussion), Claude wrote Title/Abstract/Conclusion, the draft profile reached PASS, and Codex acted as the independent semantic reviewer (round 1: 13 findings; round 2: 12 resolved, 1 escalated per Rule 9). Engine fixes found on the way:

- The edit-time lint hook ignored the paper's own terminology registry and kept flagging a term the approved plan chose ("MIS"). It now reads `terminology` from the nearest `project.json`, like `verify`.
- A freshly initialised manifest names `ai_usage.json`/`checklist.json`; before those submission records existed, `verify --profile draft` and `packet` stopped with "No such file". They are now skipped until they exist; the submission profile still blocks on them.
- `manuwright search "<query>"` works as documented (the `search` subcommand is implied).
- New user manual with screenshots: `docs/manual.md`, `docs/manual.ko.md`.
- 406 tests pass.

### v1.8.5 (260930)

Found in an end-to-end run on synthetic trial data (init, analysis plan, approval, analysis, tables, checks):

- **Template hooks silently turned off after a `cd`**: `.claude/settings.json` called `sh scripts/hooks/run.sh ...` with relative paths. Once the agent changed directory in its shell, every hook failed with exit 127, which Claude Code treats as a non-blocking error, so plan-first writes were allowed. Hook commands are now anchored to `$CLAUDE_PROJECT_DIR`. Regression test runs the gate from an unrelated folder.
- `verify` names the missing artifacts instead of "one or more declared artifacts are missing".
- Confirmed in the same run: analysis scripts blocked before the plan was approved, allowed after `record-approval`; a Results section blocked without an approved draft plan; 50 table numbers matched the results CSVs; a wrong mean (61.2) was caught with the closest true value (60.4).
- 403 tests pass.

### v1.8.4 (260930)

- **New README** in the style of popular agent-tool repositories: logo, one-line pitch, badges, before/after, how it works, install per agent, commands, workflow, FAQ (en/ko/ja/zh). Everything the old README held moved verbatim to `docs/guide/overview*.md`; changelogs moved to `CHANGELOG*.md`.
- **Logo**: a fountain-pen nib cut by a checkmark (craft + verification), made with Antigravity. `assets/logo.png` (main), `assets/logo-alt.png` (check flowing from the nib), each with a transparent dark-mode version and the original source.
- WORKFLOW Rule 12 now points version and changelog updates at the plugin manifests, README install tag and `CHANGELOG*.md`.

### v1.8.3 (260930)

- Test isolation: the installed-engine tests registered their temporary projects in the real `~/.manuwright/projects.json`. They now use a throwaway `MANUWRIGHT_HOME`. No engine change.

### v1.8.2 (260930)

- **Renamed `paperflow` to `manuwright`** ("manuscript" + "-wright", a maker, as in playwright). `paperflow` is already taken on PyPI and GitHub. Command `manuwright`, package `manuwright/`, plugin `manuwright@manuwright`, skills `manuwright` and `manuwright-verify`, settings folder `~/.manuwright`, environment variables `MANUWRIGHT_*`. Entries below keep the old name as released.
- Upgrading from v1.8.0/1.8.1: remove the old install first (`paperflow` plugins/skills in each agent, `uv tool uninstall paperflow`), then install `manuwright` and run `manuwright agents install`. Move `~/.paperflow` to `~/.manuwright` to keep the project registry and settings.

### v1.8.1 (260930)

- **Codex enforcement fix**: Codex writes files with `apply_patch` and reports the patch in `tool_input.command` (no `file_path`), so the plan-first gate never fired there. The gate and lint hooks now read every file path in the patch; hooks match `apply_patch` explicitly. Found in a live Codex session after installing v1.8.0.
- `doctor` warns about missing pytest only in a source checkout. `paperflow agents` output no longer interleaves with child output.
- 401 tests pass (+3 Codex patch tests).

### v1.8.0 (260930)

Milestone: **two-track distribution**. The same engine now runs as the clone-and-run template (Track A, unchanged) or as an installed `paperflow` CLI with adapters for Claude Code, Codex, Antigravity, opencode and Muse (Track B). Summary of v1.7.6 to v1.7.10 plus:

- README "Installation: two tracks" section; `docs/migration_guide.md` (opt-in, non-destructive migration of a copied folder; Track A update set).
- `docs/distribution_plan.md` marked implemented.
- Release tags `vX.Y.Z` are the update channel for `paperflow update`.

### v1.7.10 (260930)

- **Phase 4, agent adapters**: one install now carries a Claude Code and Codex plugin (skills `paperflow` and `paperflow-verify`, hooks for the session contract, plan-first gate, lint and style intent), a root `plugin.json` for Antigravity (`agy`), and skills for Muse and opencode. `paperflow agents install|update [--only ...] [--dry-run]` runs each agent's native command, using the installed engine folder as the plugin root so adapters always match the CLI. Plugin hooks call `paperflow hook <name>`, stay silent inside a template checkout that already runs its own hooks, warn on plugin/CLI version skew, and refresh adapters in the background when auto-update is on.
- `paperflow init` writes the shared `docs/agent_bootstrap.md` rules into `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`.
- 398 tests pass (+8 adapter tests). Validated with `claude plugin validate`, `agy plugin validate` and `muse skills validate`.

### v1.7.9 (260930)

- **Phase 3, setup and updates**: `paperflow init` (starter paper folder from the engine templates; never overwrites, never approves), `paperflow rules [keyword]`, `paperflow update [--check|--to]` (reinstalls a tagged release, logged, one-command rollback) and opt-in `paperflow config set auto-update on`. Auto-update applies patch releases only, at most once a day, and waits when a registered project pins the engine or holds a fresh semantic review/human signoff.
- Manifest `engine` pin (e.g. `">=1.8,<1.9"`); `verify` reports `engine_pin` BLOCKED on mismatch.
- 390 tests pass (+10 lifecycle).

### v1.7.8 (260930)

- Windows CI fix: two v1.7.5 tests compared snapshot keys with `/`; snapshot keys use the OS separator. Tests now build the expected key with `Path`. No engine change.

### v1.7.7 (260930)

- **Installed CLI, phase 2 (preview)**: `pyproject.toml` packages the engine as `paperflow` (`uv tool install git+...@tag`). `paperflow doctor|status|verify|packet|build|record-approval` wraps `python -m harness`; `paperflow citations|numbers|gate|lint|verify-all|search|...` wraps each script with the same flags and fills project paths from the current folder when omitted. The wheel is an allowlist (code, terminology, WORKFLOW, docs, gate template); no PDFs, profiles, drafts or data.
- `check_gate.py` / `verify_all.py`: new `--base-dir` for the project root (default unchanged).
- CI builds and installs the wheel, then runs installed-engine tests outside the package. 380 tests pass (+3 installed-only).

### v1.7.6 (260930)

- **Distribution plan** (`docs/distribution_plan.md`): two tracks from one repository. Track A keeps the clone-and-run template. Track B (planned v1.8.0) adds an installed `paperflow` CLI plus thin adapters for Claude Code, Codex, Antigravity (`agy`), opencode and Muse. Updates are checked automatically and applied explicitly, with opt-in auto-update that never stales a paper's fresh reviews. Reviewed with Codex (gpt-6-astra) and compared with Spec Kit, OpenSpec, caveman and ponytail.
- **Phase 1, compatibility contract** (`tests/test_compat_contract.py`, 22 tests): every script runs from a raw checkout and an unrelated cwd (space and Unicode path) without `PYTHONPATH`; legacy citation/number defaults stay engine-relative; the gate hook resolves the edited file from the event cwd; two manifests in one process stay independent.
- 379 tests pass.

### v1.7.5 (260929)

Improvements from a Claude + Codex (gpt-6-astra) co-review.

- **Submission records are validated field by field**: every checklist item needs a unique id, and PASS needs a manuscript location, NOT_APPLICABLE a reason; other statuses fail. Previously `{"status":"PASS"}` alone passed. When AI was used, each `tools` entry needs `tool` and `role`.
- **Abstract identity**: the manifest's `abstract` must be one of the published `artifacts`, and a published abstract file must be declared, so the check cannot test a different file or silently skip.
- **Project terminology and Style Spec**: optional `terminology` and `style_spec` manifest keys. Lint uses the project registry, `style_metrics` runs `check_style.py`, and both files enter the review snapshot.
- **Actionable failures**: harness `detail` now lists the first issues (artifact, line, value) instead of `False`. Packets include checklist/AI records and list `omitted_sources` known only by hash.
- **Preflight**: `doctor` reports `python_supported`, exercises the Claude gate hook (`hooks.ok`), and prints `warnings`. Hook errors print a WARNING instead of passing silently; `run.sh` warns when no Python exists. New `requirements-dev.txt` (used by CI).
- **Leaner context**: project tree, file-role table, command catalog and PubMed options moved from `WORKFLOW.md` (56 KB to 30 KB, loaded every session) to `docs/workflow_reference.md`. Command examples use portable `python scripts/...` paths. `/verify` example adds the `--cross-check` flags.
- 357 tests pass. `docs/harness_guide.md` v1.0.5.

### v1.7.4 (260908)

- **`profile/` templates are now shipped**: `profile/example_authors.md` (placeholder skeleton for corresponding author, co-authors, funding boilerplate, IRB/trial registry) and `profile/example_journals.md` (13 worked journal entries — in-text style, author cutoff, page range, ORCID policy, submission checklist). Copy them to `profile/authors.md` / `profile/journals.md`, which stay gitignored.
- `.gitignore`: `profile/` → `profile/*` plus negations. Git cannot re-include a file whose parent directory is excluded, so the templates were unreachable under the old pattern; real profile files remain ignored (verified).
- **Test portability fix**: `test_cli_verify_hash_resolves_relative_paths_from_project_root` hashed `drafts/05_results.md`, a fixture that only exists in this template repo — it failed in every downstream project, which lays `drafts/` out per paper. It now hashes a file the harness itself ships.

### v1.7.3 (260908)

- Verified v1.7.2 on Korean Windows: 344 tests, 9/9 CI, and 37 synthetic error-injection scenarios through the real CLI — the 25 draft/revision scenarios from v1.7.1 plus 12 new ones for `numeric_scope` (number in a non-result section without `numeric_artifacts`/exemption, empty reason, exempting a results file, exempting an already-bound file) and `revision_scope` (stale original section listed while REVn exists, CHANGE target missing from artifacts, REV2 letter with REV1 artifacts). All blocked/passed as designed.
- `docs/project.example.json`: add the `numeric_exemptions` key so the new v1.7.2 field is discoverable from the template manifest.
- README ko/ja/zh: localize the v1.7.2 changelog entry (was English-only). Headers → v1.7.3; `harness/__init__.py` (doctor) → 1.7.3; `docs/harness_guide.md` → v1.0.3.

### v1.7.2 (260907)

- Bind revision claims and latest section versions to the actual submission files.
- Reject unchecked numerical artifacts; require explicit reasons for non-result exclusions.
- Detect p-value table columns even when headers contain numbers; preserve header number checks.
- Synchronize doctor version and add regression tests for submission scope.

### v1.7.1 (260908)

**Post-merge verification of v1.7.0 (PR #1) — 4 defects fixed, doc sync**

- **CI never ran on v1.7.0.** `.github/workflows/tests.yml` had the OS-matrix line nested under setup-python `with:`, so every run died at workflow-parse time (0 s). The 3-OS × 3-Python matrix now executes (9/9 green on main).
- **Windows cp949:** the new `test_harness.py` / `test_review_regressions.py` read files without `encoding='utf-8'` → 3 failures on Korean Windows, hidden by the dead CI. Fixed; 333 tests pass.
- **Build filenames:** `harness build` stamped the UTC date (yesterday's `_YYMMDD` between 00:00–09:00 KST) and omitted `_REVn` for revision packages (Rule 5). Now `manuscript_YYMMDD.docx` for initial submissions and `manuscript_REV1_YYMMDD.docx` / `response_letter_REV1_…` / `table_N_REV1_…` for revisions. Synthetic REV1 build test added; `docs/harness_guide.md` v1.0.1.
- **`CLAUDE.md` now imports `WORKFLOW.md`** (`@WORKFLOW.md`), so Claude Code auto-loads the shared rules instead of relying on a "read it first" instruction. Stale "CLAUDE.md is the core-rules file" references in `WORKFLOW.md`/README updated to `WORKFLOW.md`.
- Verified end-to-end on synthetic projects through the real CLI: 12 draft-profile and 13 revision-profile error-injection scenarios (unregistered citation, `todo` evidence, number not in CSV, plan edited after approval, ghost revision, unanswered/placeholder response, REV2-vs-REV1 baseline) were all blocked as designed; DOCX structure matches `docs/docx_guide.md`.

### v1.7.0 (260906)

- Fixed F01–F09: citation status/duplicate IDs, p-value bounds, placeholders, gate identity, plan completeness, revision baseline and reviewer fallback.
- Added shared WORKFLOW.md, standard AGENTS.md and GEMINI.md bootstraps.
- Added manifest-based verification profiles, context-bound results, content-bound approvals, review packets/state, and gated DOCX packaging.
- See [shared engine guide](docs/harness_guide.md) for setup, migration and remaining limits.

### v1.6.4 (2026-08-30)

**Full harness review (Claude Fable) — 16 defects fixed, 33 regression tests**

- **Gate false-PASS / false-FAIL / crash (HIGH):** `check_citations.py` now FAILs malformed or non-ASCII `[EVID:…]` tags (`o'brien_2021`, `müller_2020`) instead of silently reporting PASS with 0 tokens; `search_pubmed.py` slugifies generated ids and uses the full last name. `check_numbers.py`: a ragged results-CSV row no longer crashes the gate; manuscript `p<0.001` matches a CSV cell `<0.001` (same or looser bound); uppercase `P<0.05` is a p-comparison; spine-level / code-style suffixes (`L4-5`, `C5-6`, `COVID-19`, `ICD-10`) are structural, not results; ROUND_HALF_UP accepted alongside banker's rounding (2.675 → 2.68).
- **Enforcement actually on across platforms:** hooks run via new `scripts/hooks/run.sh` (`py` if present, else `python3`) — previously every hook exited 127 on macOS/Linux and Rule 7/8 was silently off. `enforce_gates.py` now also rejects a plan with *no* approval checkbox (Rule 9 wording was not enforced).
- **`check_gate.py`:** artifact paths compared slash-insensitively (`drafts\05_results.md` == `drafts/05_results.md`, incl. `--verify-hash` / `--cross-check`); multi-block gate files are split per `artifact:` and `--artifact` selects the block — an earlier block's FAIL can no longer be masked by a later PASS; multiple blocks without `--artifact` fail loudly. `_TEMPLATE.GATE.md` documents this.
- **`check_response_coverage.py`:** citation-shaped brackets (`[12]`, `[3-5]`, `[EVID:id]`) are no longer treated as placeholders — rebuttals citing literature pass.
- **Minor:** `check_abstract.py` half-up rounding; `format_references.py` accepts `author_year_keyword` ids in author-year mode (docs aligned: `evidence_guide.md` v0.3.1); `compile_response_docx.py` no longer rewrites "# Response to Reviewers" as "Response: to Reviewers"; line numbers after code fences correct in `check_citations` / `check_numbers` / `check_coverage`; `check_coverage.py` counts markdown-table rows separately; `check_abbreviations.py` allowlist matches `COVID-19` via stem; `lint_manuscript.py` catches italic `*p* = .02` and stops flagging "group = 30".
- Tests 262 → 295.

### v1.6.3 (2026-07-02)

**Mechanical submission-error checkers (advisory-first)**

- **`scripts/check_crossrefs.py`** — verifies in-text "Table N"/"Figure N" mentions against the actual `table_*.md` files and figure-legend entries: broken references (the desk-reject trigger nothing else caught), unreferenced tables/figures, and out-of-order first mentions. Handles "Tables 1 and 2", "Figure 2-4", "Fig. 1A"; ignores code fences/HTML comments; skips a kind loudly instead of flagging everything when its inventory is missing. Advisory by default; `--fail-on-broken` / `--fail-on-unreferenced` / `--fail-on-order` to gate.
- **`scripts/check_abbreviations.py`** — define-at-first-use audit with abstract and body as independent scopes (journals require both). Emits `ABBREV_UNDEFINED` / `ABBREV_DEFINED_AFTER_USE` / `ABBREV_REDEFINED` / always-advisory `ABBREV_SINGLE_USE`. Deliberately advisory — detection is capitals-only (2-6 letters, `-digits`, plural `s`) with a built-in statistical allowlist (CI, SD, OR, HR, ...) extendable via `--allow`; `--strict` gates definition issues only.
- **`scripts/check_response_coverage.py`** — the opposite face of the ghost-revision gate: did the response letter answer **every** reviewer comment? Parses the `Reviewer #N:` / `Comment N)` / `Response:` structure, blocks missing/empty/`[placeholder]` responses, and with `--comments` cross-checks the original reviewer_comments file (`COMMENT_UNANSWERED` fails; unparseable original warns, `--strict` fails). Fails by default — a skipped comment is binary.
- Design principle per author feedback: mechanization only for binary facts; judgment stays human+LLM. Docs updated (`CLAUDE.md`, `docs/qc_guide.md` §3.7/§4.2, `docs/revision_guide.md`). 40 tests (262 total).

### v1.6.2 (2026-07-02)

**Abstract Keywords enforced**

- The `**Keywords:**` line at the bottom of `drafts/02_abstract.md` was easy to miss (no lint, no explicit rule). Three-layer enforcement: (1) the template now names the requirement and gives an example, (2) `docs/writing_guide.md` § 02. Abstract lists a Keywords rule (3-6 MeSH-preferred terms, semicolon-separated), and (3) `scripts/lint_manuscript.py` detects abstract files and emits `KEYWORDS_MISSING` / `KEYWORDS_EMPTY` / `KEYWORDS_TOO_FEW` / `KEYWORDS_TOO_MANY` — the PostToolUse `lint_on_edit` hook already surfaces lint on edits, so an empty Keywords line is now caught the moment the abstract is touched. Semicolon and comma separators both counted. 7 tests (222 total).

### v1.6.1 (2026-06-30)

**`/editor-review` uses the same reviewer picker as `/critical-review`**

- The editorial desk-screen now offers the identical model-selection UX as `/critical-review`: an `AskUserQuestion` reviewer picker over the same pool — the four OpenRouter models (`scripts/critical_models.txt`) + local Claude + Codex — only the role differs (`--role editor`, prompt `editor.txt`). Selecting just `Claude` gives the single Opus subagent (no key). Codex is orchestrated via `codex:codex-rescue` (it is not a `critical_review.py` model — that script handles OpenRouter + local Claude). Command + protocol §5 updated; also fixes the ja/zh README headers that were left at v1.5.10 while their changelog already listed v1.6.0.

### v1.6.0 (2026-06-29)

**Editorial desk-screen — high-impact-journal editor assessment (`/editor-review`)**

- A new evaluation that goes beyond mechanical QC and reviewer-level critique: an **Editor-in-Chief / Clinical Editor desk-screen at the high-impact tier**. It identifies the manuscript's own field, benchmarks the paper against what that field's high-impact journals actually publish, and judges **clinical validity** (practice-changing? MCID/effect, not just p?), **scope/novelty fit**, and **methodological/analytic adequacy** — then returns a `SEND FOR PEER REVIEW` / `BORDERLINE` / `DESK REJECT` verdict with the concrete **additional validation needed to compete**, or a realistic lower-tier journal if the bar is out of reach.
- Canonical prompt `scripts/critical_prompts/editor.txt` (single source). Runs as a single Opus subagent (no API key) **or** a multi-model panel via `scripts/critical_review.py --role editor`; optional medical-kag / PubMed benchmark of the real high-impact literature. Exposed as `/editor-review`; documented in `docs/critical_review_protocol.md` §5. Advisory (judgment-based) — does not replace the grounded gates. Tests added.

### v1.5.10 (2026-06-28)

**Test-coverage hardening, round 2 (MEDIUM gaps)**

- Added tests for the remaining coverage gaps from the full review: `search_pubmed.py` pure formatters (`format_citation` author-count branches, `guess_study_design` ladder); `check_abstract.py` (abstract more precise than body → fail, integer match, multi-file body aggregation, comparator preserved in the issue); `check_numbers.py` (p-value `>` comparator pass/fail, `is_structural_number` for heading/`Table N`/`Figure N`/bare-year); `check_style.py` (`mean_sentence_length`/`paragraph_count` tolerance, `split_sentences` abbreviation/decimal protection); `check_citations.py` (`require_citations`, `fail_abstract_only` toggles); `format_references.py` (`smith_2020a` disambiguation, `--convert` write path); `check_coverage.py` (`--fail-on-unrealized`). 214 tests total (was 170).

### v1.5.9 (2026-06-28)

**Test-coverage hardening on enforcement paths**

- A full-review coverage analysis found that several *enforcement contracts* had no test, so a regression could silently disable them. Added tests for: `verify_all.py` top-level `OVERALL: PASS` verdict and its `--cross-check` (+ `--evidence`/`--results`) pass-through to `check_gate.py`; `check_coverage.py` exit codes for `--fail-on-over-citation` / `--fail-on-unknown` / `--fail-on-uncited-verified` (advisory-by-default vs blocking); and `check_revision_claims.py` `--strict` escalation (a missing original section is a warning by default, a failure under `--strict`). 170 tests total (was 163).

### v1.5.8 (2026-06-28)

**Unify the `[EVID:id]` regex (full-review consistency fix)**

- `extract_claims.py` defined its own permissive `[EVID:([^\]]+)]` pattern while `check_citations.py` (and the scripts that reuse it — `check_coverage.py`, `format_references.py`) use the restrictive `[A-Za-z0-9_.-]+`. Valid slugified ids match both identically, but the drift meant a malformed tag could be extracted yet not validated/converted. `extract_claims.py` now imports the canonical `EVID_RE` from `check_citations.py`, so all four scripts share one source of truth. No behavior change for valid ids; 163 tests green.

### v1.5.7 (2026-06-28)

**Bug fixes from a full code audit**

- **Gate cross-check now fails on any live FAIL** (`check_gate.py`) — previously, if a cross-checked dimension failed the live re-run *and* the ledger also recorded FAIL, the gate treated that as "consistent" and did not add a failure, so a broken artifact could still pass when the dimension was not also a `--require-check`. A live deterministic failure now always fails the gate, regardless of the ledger.
- **Plan-first hook no longer fails open on a relative cwd** (`hooks/enforce_gates.py`, `hooks/lint_on_edit.py`) — a relative/missing `cwd` normalized the path to e.g. `drafts/05_results.md` (no leading slash), so the `"/drafts/"` / `"/data/.../py/"` checks did not match and the Rule 7/8 gate was skipped. Paths are now normalized to a leading slash before the check. (Latent: production always sends an absolute cwd.)
- +2 regression tests (163 total).

### v1.5.6 (2026-06-28)

**Abstract↔body number consistency + medical-kag synthesis workflow**

- **`scripts/check_abstract.py`** — checks that every number stated in the abstract also appears somewhere in the body sections (rounding-tolerant), catching the classic reviewer complaint of an abstract-only figure. Complements `check_numbers.py` (which ties numbers to `results/*.csv`); p-value tokens are excluded by default (`--include-p-values` to include). Automates the Abstract↔Methods↔Results↔Tables consistency that Rule 3 / QC Round 1 require. 5 tests.
- **medical-kag synthesis → Discussion/Limitations workflow** (`docs/medical_kag_protocol.md`) — `compare_interventions` / `conflict synthesize` output is rich but noisy (bibliometric outcomes, empty values, KG-normalized names); documents how to filter to clinical outcomes, ground every number/citation, and gate the result, with a Discussion/Limitations skeleton.

### v1.5.5 (2026-06-28)

**CI: run the test suite on every push/PR**

- **`.github/workflows/tests.yml`** — GitHub Actions runs the full pytest suite on pushes to `main` and on pull requests, across Python 3.10 / 3.11 / 3.12, so a change that breaks any verification script is caught before it lands. A status badge is shown at the top of the README.

### v1.5.4 (2026-06-28)

**MCP-independent reference formatter (Phase 7)**

- **`scripts/format_references.py`** — converts drafting-time `[EVID:id]` tags into a submission-ready reference list and in-text citations, reading only `knowledge/evidence.md` (no medical-kag required). Two styles: **numbered** (Vancouver — `[EVID:id]` → `[N]` by first appearance, list numbered in that order) and **author-year** (`(Author, Year)`, alphabetical list). `--convert` writes each section with tags replaced to a sibling `*_formatted.md` (never in place); a cited id absent from evidence.md is left unconverted and reported (and makes the run non-zero). Complements the medical-kag `reference` tool, which stays available when connected. 7 tests (156 total).

### v1.5.3 (2026-06-28)

**Coverage audit refocused on over-citation (not orphan-as-waste)**

- **Over-citation detection** — `check_coverage.py` now flags sentences carrying more than `--max-citations-per-sentence` (default 4) `[EVID:id]` citations (citation stuffing / padding). This and **unknown citations** are the real quality signals; `--fail-on-over-citation` / `--fail-on-unknown` are the meaningful blocking flags.
- **Reframed orphan/uncited as neutral** — an uncited-but-registered reference is normal curation (you cite only what is necessary), **not** wasted work. The prior "verified work unused" framing is removed; uncited refs and unrealized draft_plan items are reported as neutral information. `--fail-on-uncited-verified` / `--fail-on-unrealized` remain only for strict full-use policies and are off by default. Coverage tests now total 8 (149 suite-wide).

### v1.5.2 (2026-06-27)

**Citation coverage / orphan audit**

- **`scripts/check_coverage.py`** — a Phase 6 QC audit against `knowledge/evidence.md`: reports **orphan references** (registered but never cited; verified-but-uncited flagged as wasted work), **citation density** per manuscript section, **unknown citations** (cited but unregistered), and — with `--draft-plan` — **unrealized claims** (planned in the Claim→Citation map but never cited in the body). Advisory by default; `--fail-on-orphan-verified` / `--fail-on-unrealized` / `--fail-on-unknown` make any dimension blocking. Reuses `check_citations.py` parsing so the two stay in lockstep. 7 tests (148 total).

### v1.5.1 (2026-06-26)

**Translated-README documentation-table parity**

- Added the missing File Roles rows to the Korean/Japanese/Chinese READMEs so they match `README.md`: `docs/debate_protocol.md` and `docs/critical_review_protocol.md` (all three), plus `scripts/critical_review.py` (ja/zh). Docs-only; no code change.

### v1.5.0 (2026-06-26)

**Gate cross-check (ledger ↔ live) + doc/version auto-sync policy**

- **Gate cross-check** (`scripts/check_gate.py --cross-check LABEL=PATH`) — re-runs the canonical checker live for the deterministic dimensions (`citation` / `numbers` / `revision_claims`) and fails the gate when the ledger's recorded status disagrees in either direction, catching a stale or fabricated `PASS`; loud-fails when a source is unreachable. Forwarded by `scripts/verify_all.py` and wired into the canonical gate commands (`review/gates/_TEMPLATE.GATE.md`, `docs/verification_protocol.md` v0.3.0, CLAUDE.md). +6 regression tests (141 total).
- **Doc/version sync + auto commit-push policy** (CLAUDE.md Rule 12) — every harness code/bug change now bumps the version, updates the affected docs, and auto-commits/pushes (with explicit STOP conditions for sensitive or destructive cases).

### v1.4.1 (2026-06-24)

**Template-gate hardening + `/verify` freshness forwarding**

- **Template-aware plan gates** — `scripts/hooks/enforce_gates.py` now treats unresolved `analysis_plan.md` / `draft_plan.md` templates or unchecked approval boxes as not approved, applies to `Write|Edit|MultiEdit`, and avoids false positives for legitimate citation-style `[N]` text.
- **Fresh `/verify` gate checks** — `scripts/verify_all.py` now forwards `--verify-hash` to `check_gate.py`; README/CLAUDE/slash-command examples include freshness inputs.
- **Windows/template hygiene** — PubMed command examples use `python scripts/search_pubmed.py`, generated root-level DOCX artifacts are ignored, and regression tests cover the new hook and freshness-forwarding behavior.

### v1.4.0 (2026-06-24)

**Citation stance + evidence comparison table (GraphRAG-backed)**

- **Citation stance** (`/cite-stance [claim|section]`) — classify how each cited source relates to a claim (supporting / contrasting / mentioning) so the Discussion stays balanced; flags "one-sided" when contrasting evidence exists but is not cited (overclaim-by-omission guard). New Citation-Stance verifier (`docs/verifier_prompt_templates.md`); medical-kag `conflict` surfaces missing contrasts, evidence.md fallback. Scite-style, claim-specific.
- **Evidence comparison table** (`/evidence-table [topic|ids]`) — assemble a "summary of included studies" table (study / design / n / intervention / outcome / result / LoE) for the Discussion or a PRISMA supplement. `scripts/evidence_table.py` is the deterministic formatter; medical-kag structured data primary, evidence.md fallback. Elicit-style. Tests added.

### v1.3.0 (2026-06-24)

**Citation assist — suggestion + per-claim verification (GraphRAG-backed)**

- **Citation suggestion** (`/suggest-citation [claim]`) — given a draft claim, retrieve the best `[EVID:id]` candidates via the medical-kag knowledge graph (GraphRAG), falling back to `knowledge/evidence.md` + `scripts/search_pubmed.py` when the MCP is unavailable. The author picks; new sources are registered in evidence.md (PMID/DOI verified) before they become citable, so grounding holds.
- **Per-claim verification report** (`/verify-claims [section]`) — `scripts/extract_claims.py` pulls every `[EVID:id]`-tagged sentence, then the Semantic-Citation Verifier classifies each as SUPPORTED / PARTIAL / UNSUPPORTED into `review/claim_verification.md` (a Phase-6 QC "claim map", deeper than `check_citations.py`'s existence check). New `docs/citation_assist_protocol.md`; both operations degrade gracefully to evidence.md. Tests added.

### v1.2.0 (2026-06-22)

**medical-kag MCP integration — knowledge graph alongside evidence.md**

- **Grounding-preserving KAG integration** — the `medical-kag-remote` MCP (a spine-surgery knowledge-augmented graph) plugs in as an upstream discovery/analysis/format engine, while `knowledge/evidence.md` stays the single canonical citation ledger: anything the graph surfaces is registered as `[EVID:id]` (PMID/DOI verified) before it can be cited, so `check_citations.py` still gates everything. New `docs/medical_kag_protocol.md` maps the tools to phases — discovery + structured extraction (Phase 1), evidence-chain / intervention-comparison / GRADE synthesis for claims + Discussion (Phase 3-4), conflict / overclaim guard (Phase 6), journal-style reference lists (Phase 7).
- **Additive + fallback** — the MCP is never a dependency: if it is unavailable (e.g. an unauthenticated remote session), the workflow degrades to `scripts/search_pubmed.py` + manual evidence.md. Wired into CLAUDE.md (Rule 1, STOP signals, Phase 1, Quick Commands) + AGENTS.md for Codex parity.

### v1.1.2 (2026-06-21)

**Fix — hooks read UTF-8 stdin (Korean intent on Windows)**

- The `UserPromptSubmit` / `PreToolUse` / `PostToolUse` hooks now reconfigure stdin to UTF-8. On Windows (cp949 default) the JSON payload Claude Code emits was mis-decoded, so non-ASCII prompts — e.g. the Korean auto-trigger "학술적으로 바꿔줘" — silently failed to match. Added an end-to-end UTF-8 stdin test.

### v1.1.1 (2026-06-21)

**Style enforcement — measurable gate + Codex parity**

- **Deterministic style metrics** — `scripts/check_style.py` (`extract` / `check --spec`) measures word count, mean sentence length, paragraphs, citation density, and hedging, and flags deviations from the Style Spec targets — the "check_numbers for style". Wired into `lint_on_edit.py` (surfaces `[STYLE-METRIC]` deviations on each draft edit when a Style Spec exists) and the Phase 5/6 gates. Tests added.
- **Codex parity + calibration** — `AGENTS.md` now tells non-Claude runtimes to run the style-pass (`check_style.py` + Style-Conformance verifier) explicitly, since the hooks are Claude Code-only. The Style Spec template gains a before→after calibration example (few-shot steers the transform better than abstract rules).

### v1.1.0 (2026-06-21)

**Style transformation — rough draft → bound journal style, reliably**

- **Style Spec + Style-Conformance Verifier** — bind ONE exemplar (`Style/own/` or `Style/target_journal/`) into a compact, always-loaded `drafts/style_spec.md` (`docs/style_spec_template.md`), then transform section-by-section and verify each section against the spec with an independent **Style-Conformance Verifier** (auto-fix loop, max 2; `docs/verifier_prompt_templates.md` + `verification_protocol.md`). This reaches the holistic style layer (structure, sentence length, hedging, claim strength, reference format) that lint cannot. New `/style-pass` command + `docs/style_transform_protocol.md`.
- **Auto-trigger on intent** — a `UserPromptSubmit` hook (`scripts/hooks/style_intent.py`) detects "make it academic / 학술적으로 바꿔줘" and injects the style-pass protocol, so the transform fires without remembering the command. SessionStart now also surfaces the active Style Spec. Advisory + fail-open. Tests added.

### v1.0.3 (2026-06-20)

**Cross-runtime critical review + model selection**

- **Claude-CLI reviewer** — `scripts/critical_review.py --include-claude` shells out to the local `claude -p` (headless) so a non-Claude-Code caller (Codex or a plain shell) can pull in Claude's adversarial review. `OPENROUTER_API_KEY` is now only required when an OpenRouter model is actually requested. Documented in `docs/critical_review_protocol.md` + `AGENTS.md`.
- **Larger model pool + pick ~2** — `scripts/critical_models.txt` now offers MiniMax M3, GLM 5.2, Qwen3-Max, and DeepSeek V4 Pro; `/critical-review` presents them as individual `AskUserQuestion` options and recommends choosing ~2 (cost + blind-spot diversity), then runs `--models <selected>`.

### v1.0.2 (2026-06-20)

**Process enforcement + CLAUDE.md condensation**

- **Plan-first enforcement (hooks)** — `.claude/settings.json` adds committed hooks: a PreToolUse `Write|Edit|MultiEdit` gate (`scripts/hooks/enforce_gates.py`) that BLOCKS drafting a section without a completed/approved `drafts/.../draft_plan.md` (Rule 8) or creating an analysis script without a completed/approved `data/.../analysis_plan.md` (Rule 7), and a SessionStart hook (`scripts/hooks/session_contract.py`) that injects the workflow contract every session. Revisions are exempt; multi-paper subfolders handled; fails open; UTF-8 safe. (Windows `py`; macOS/Linux use `python3`.)
- **`/verify`** — `scripts/verify_all.py` runs check_citations + check_numbers (+ optional check_gate) in one command before recording a gate PASS, and forwards `--verify-hash` to keep documented freshness checks active. Hook and freshness-forwarding behavior is covered by regression tests.
- **CLAUDE.md condensed 808 → 696 lines (~14%)** — collapsed the Multi-Paper/Revision structure trees and the Phase-2 Notes / test-selection / style-priority / gate-placement duplicates into pointers to their canonical docs; no MUST-FOLLOW rule removed.

### v1.0.1 (2026-06-20)

**Post-release hardening + concision tooling**

- **Same-day hardening (code review + project audit)** — `check_gate.py` freshness now fails cleanly on non-file paths (directory/missing) instead of crashing, anchors relative paths on the repo `ROOT`, rejects blank/placeholder digests with a clear message, and reports `provenance_verified` / `provenance_unverified` in PASS output; Phase 8 verifier set aligned (Logic is Draft-only; Revision adds Revision-claims + Response-alignment) with `--require-check constraint` in the gate commands; "3 verifiers" corrected to "4"; Critical Rules renumbered 9/10/11; `lint_manuscript.py` skips nonexistent `.md` arguments (first lint tests added); `check_numbers.py` requires an explicit p-value (not any 0–1 proportion); `search_pubmed.py` evidence entries gain Evidence ID + Source Status; `failure_code` added to checker FAIL output; test suite expanded to 77 tests.
- **Concision Pass** — `docs/writing_guide.md` gains a journal word-limit compression pass (Phase 5): 10 Before→After patterns distilled from a senior English edit, plus an over-compression guardrail (keep primary-outcome definitions, statistical spec, eligibility, and key limitations in text or move to Supplement — never silently delete).

### v1.0.0 (2026-06-20)

**Verification hardening (superpowers-inspired)**

- **Gate freshness / provenance** — `check_gate.py` gains a `provenance:` block (sha256 of artifact/evidence/results), `--verify-hash LABEL=PATH` (fails a gate as *stale* when a verified file changed after PASS), and `--compute-hash PATH`. Closes the stale-PASS hole opened by parallel verification; backward compatible (opt-in flag). `review/gates/_TEMPLATE.GATE.md` and `docs/verification_protocol.md` (v0.2.0) document it; pytest coverage expanded to 70 tests.
- **Parallel verifiers + Constraint-first** — the four section-gate verifiers run concurrently against a frozen artifact; fixes prioritize Constraint (spec) violations; all PASSes are discarded and re-run after any edit (`docs/verification_protocol.md`).
- **STOP signals** — CLAUDE.md anti-rationalization table (§10) guarding the human-level shortcuts verifiers miss.
- **Socratic draft-plan brainstorming** — `docs/draft_plan_template.md` Step 0 (one question at a time; distinct from `/paper-debate`, feeds it as R0 prep), wired into CLAUDE.md Phase 3 + Rule 8.
- **Reviewer-response triage** — `docs/revision_guide.md` accept/partial/rebut posture per comment, tied to `[CHANGE]` + ghost-revision; Phase 8 verifier set aligned to include Constraint.
- **Command `use-when` lines** added to `.claude/commands/*.md`; TodoWrite documented as non-authoritative QC/gate tracking (CLAUDE.md Rule 4).

### v0.9.3 (2026-06-19)

**Co-author collaboration and multi-model critical review**

- Added **`/paper-debate`** (`docs/debate_protocol.md`, `.claude/commands/paper-debate.md`) — pre-writing Claude–Codex co-author debate for analysis plans, draft plans, argument structure, and reviewer responses; bounded rounds with consensus cap 3, debate logs under `review/debates/`, Claude-solo fallback.
- Added **`/critical-review`** (`docs/critical_review_protocol.md`, `.claude/commands/critical-review.md`) — post-writing adversarial review by any combination of a fresh Claude subagent, Codex, and OpenRouter models (default `minimax/minimax-m3`, `z-ai/glm-5.2`), merged and ranked by consensus × severity, reports under `review/critical/`.
- Added `scripts/critical_review.py` (OpenRouter caller; one model's failure is skipped, not fatal), `scripts/critical_models.txt` (externalized model list), and `scripts/critical_prompts/` (single-source adversarial prompts `manuscript.txt` / `response.txt` shared by the script, the Claude subagent, and Codex).
- Critical-review prompts framed at **senior peer-reviewer / editor-in-chief level** — design soundness, data-to-conclusion support, and publication-worthiness, not just surface defects.
- `build_prompt` uses `str.replace` (not `str.format`) so literal braces (JSON/LaTeX examples) in a prompt or target text cannot crash substitution; regression test added.
- Added **AI-Draft De-bloat** section to `docs/writing_guide.md` — strips AI tells (hollow `-ing` analysis, AI vocabulary, signposting) while excluding legitimately conflicting patterns (hedging/copula/passive).
- OpenRouter access via `OPENROUTER_API_KEY` in `.claude/settings.local.json` (gitignored); absent key skips OpenRouter and proceeds with the other reviewers.
- CLAUDE.md integrates both commands (Collaboration commands, Phase 2/3/4/8 debate prompts, Round 6 two-layer critical review, File Roles, structure trees).

### v0.9.2 (2026-06-18)

**Verification harness hardening** (bug fixes + doc consistency)

- `check_numbers.py`: no longer crashes on percentages (e.g. 42.5%); rejects p-values backed only by an unrelated value (e.g. a count of 0); handles thousands separators (1,234) and ignores ISO dates and inline `code` spans.
- `check_gate.py`: strips inline `# ...` comments so the documented gate template passes and round-overflow escalation works.
- Added `requirements.txt` (python-docx) and a `tests/` pytest suite (run with `pytest`).
- Docs: verifier set corrected to Constraint / Citation / Data / Logic (Revision adds Revision-claims and Response-alignment); response compiler description corrected (it reproduces formatting, it does not read a reference .docx).

### v0.9.1 (2026-06-18)

**Multilingual README and Author Response DOCX Completion**

- Synchronized English, Korean, Japanese, and Chinese READMEs with the verification harness scripts and DOCX response workflow.
- Added Author response Markdown template documentation and `compile_response_docx.py` usage.
- Added deterministic checker references for citation evidence, numeric grounding, phase gates, and revision claims.
- Added LLM verifier prompt-template documentation for hallucination control, redundancy control, logic checks, and revision alignment.

### v0.9.0 (2026-06-16)

**Verification Harness** — inline produce→verify→fix→re-verify gates (new `docs/verification_protocol.md`)

- Inline verification gates after each produce step (Phase 3/4/8) — replaces end-loaded manual QC with a produce→verify→fix→re-verify loop
- Verifier subagents: Constraint (instruction compliance), Citation (citation grounding vs evidence.md), Data (numbers vs results CSV), Logic (cross-section logic/redundancy); the Revision gate adds Revision-claims and Response-alignment
- Autonomous fix loop (max 2 retries) then user escalation
- `[EVID:author_year]` citation tags and results-CSV-as-single-source grounding
- Gate ledger (`review/gates/`) blocks progress until `status: PASS` is recorded
- `evidence.md` entries gain a Source Status field; Phase 6 QC lightened to a final-confirmation pass
- Programmatic citation checker: `python scripts/check_citations.py drafts/03_introduction.md --evidence knowledge/evidence.md`
- Programmatic number checker: `python scripts/check_numbers.py drafts/05_results.md drafts/table_1.md --results results`
- Programmatic phase gate checker: `python scripts/check_gate.py review/gates/phase_04_draft.GATE.md --artifact drafts/05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts/05_results.md`
- Programmatic ghost-revision checker: `python scripts/check_revision_claims.py drafts/revision/REV1/response_letter_REV1.md --strict`
- LLM semantic verifier schema: `docs/verifier_prompt_templates.md` for logic, redundancy, semantic citation support, and revision-response alignment

### v0.8.1 (2026-06-16)

**Response Letter Formatting Rules** — `docs/revision_guide.md` internal version v0.3.0 → v0.4.0

- Reworked the response letter format to a minimal-formatting standard:
  - Bold only the words **"Comment x.x"** and **"Response"**; all other formatting removed (no headings, colors, indentation, tables, or bullet/numbered lists)
  - Quoted revised manuscript text is set in *italic*
  - Responses are written as prose (no numbered/itemized points), flowing thanks → position → rationale → action in a single paragraph
  - Revision locations use lead-in placement — state the location first, then quote the revised text (no trailing "(See ...)")
  - No hyphens or em-dashes
  - Persuasive, reviewer-convincing tone
- Added a **minimal change principle** for manuscript edits — make only the smallest sentence changes needed to address each comment, keeping revisions concise rather than verbose
- Updated the "during writing" checklist to match the new formatting rules

### v0.8.0 (2026-06-16)

**Style Workflow, Linting, and Agent Instructions**

- Promoted writing-style material into the top-level `Style/` workflow, separate from reference evidence under `knowledge/`.
- Added `Style/style_guide.md` for style-anchor extraction rules, PDF-to-MD mirror rules, and publisher generic filename handling.
- Expanded `Style/terminology.md` into the project terminology registry for preferred/forbidden terms across spine surgery, trials, AI/radiomics, and reporting contexts.
- Added `docs/drafting_protocol.md` and `docs/section_templates.md` to enforce outline → evidence-bound draft → style pass → QC drafting.
- Added `scripts/lint_manuscript.py` and updated draft/table templates so manuscript linting passes with `python scripts/lint_manuscript.py drafts --quiet` on Windows.
- Added `AGENTS.md` as agent bootstrap instructions, with `CLAUDE.md` as the authoritative source of truth.
- Updated `.gitignore` so copyrighted PDFs and private style-anchor summaries remain local, while public workflow files and examples remain commit-eligible.

### v0.7.1 (2026-05-15)

**Terminology & Template**

- Added `Style/terminology.md` — field-standard terminology registry for BESS/spine surgery
  - Correct vs incorrect usage for 60+ terms across: procedure names, instruments, outcome measures, study design, statistics, complications
  - Common mistake list (creatine phosphokinase vs creatinine kinase; assessor-blind vs double-blind; VAS vs NRS; etc.)
- Added `docs/draft_plan_template.md` — complete 10-item draft plan template
  - Claim→Citation Mapping tables (Introduction/Methods/Discussion)
  - Approval checklist (all 10 items must be complete before Phase 4)
- CLAUDE.md Phase 1: Added journals format check and Style anchor review at project setup
- CLAUDE.md: Updated File Roles table, Phase 3 workflow, and Quick Commands to reference template
- Fix: `profile/journals.md` citation examples corrected — TSJ now shows 6 authors before et al. (not 3); BJJ now lists all 8 authors without et al. (per BJJ policy)

### v0.7.0 (2026-05-14)

**Citation Quality & Style Consistency**

- Added `Style/` — own, landmark, and target-journal style anchors
  - 2018 Spine — Depression & chronic LBP cross-sectional (KNHANES)
  - 2020 Spine J — Biportal endoscopic vs microscopic laminectomy RCT
  - 2023 Spine J — Biportal endoscopic vs microscopic discectomy RCT
  - 2024 Neurospine — BESS safety profile: pooled analysis of 2 RCTs
  - 2025 Bone Joint J — ENDOBH multicentre RCT (6 hospitals)
  - Each file: full citation, key terminology table, methods boilerplate, key claims with data
- CLAUDE.md Rule 8: Added **Claim→Citation Mapping** as required item 10 in draft_plan.md
  - ~20 key claims mapped to citations before writing starts
  - Intro background (5–8), methods rationale (2–3), discussion comparisons (5–8)
- CLAUDE.md: Phase Completion Criteria 3→4 updated (9 → 10 required draft_plan items)
- Added `profile/journals.md` (local only, gitignored) — verified citation formats for 8 target journals
  - The Spine Journal: bracket [N], 6 authors then et al.
  - Spine (Phila Pa 1976): superscript, "(Phila Pa 1976)" required in citation
  - Bone Joint J: all authors listed, Vol-B(issue) format
  - Neurospine: superscript, et al. after 3 authors
  - Also: J Neurosurg Spine, Global Spine J, Clin Orthop Relat Res, Asian Spine J
- Added ORCIDs for 5 co-authors in `profile/authors.md` (local only, gitignored)

### v0.6.0 (2026-04-18)

**Writing Guide Major Refactor** — `docs/writing_guide.md` internal version v0.3.0 → v0.4.0

- **Role separation** between CLAUDE.md (orchestrator) and writing_guide.md (rules)
  - CLAUDE.md "Natural Academic Writing Style" section collapsed to pointer-only (~115 lines removed)
  - All writing style rules, tables, and examples consolidated in writing_guide.md
- **New section: Style Reference Tables** in writing_guide.md
  - Voice & Tense by Section (6 sections: Abstract/Intro/Methods/Results/Discussion/Conclusion)
  - Transition Words (but → nonetheless)
  - Verb Upgrades (showed → demonstrated)
  - Common Corrections (elderly → older adult, etc.)
  - Statistical Notation (italic *p*, en-dash for ranges, never *p* = 0.000)
  - Hedging Language (4-level guide: Strong/Moderate/Weak/Very weak for Discussion)
- **New section: Writing Principles (4 Pillars)** in writing_guide.md
  - Clarity, Conciseness, Objectivity, Consistency with expanded examples
- **General Principles expanded** with 6 new rules:
  - No bold text in manuscript body
  - Abbreviation define-once rule
  - Clinical findings as sentence subject (not statistical method)
  - No synonym mixing (dural tear ↔ durotomy, etc.) with draft_plan.md term selection
  - Numerical formatting consistency (decimals, units)
  - No sentence-initial numbers (spell out or restructure)
- **Results section**: added non-significant p-value omission guideline (primary outcome exception)
- **Discussion section**: three new subsections
  - No specific numbers/p-values (literature comparison exception)
  - No directional-trend framing for non-significant results
  - Neutral tone with banned exaggeration list
- **Tables section**: 2 new Tips
  - Methods Statistics vs Table footnote role separation
  - Supplementary Table for pre-specified sensitivity analyses

**Cross-file Consistency Fixes**

- CLAUDE.md Phase 2: explicit reference to `docs/statistical_analysis_guide.md` + `analysis_plan.md` required items (endpoint hierarchy, tests, multiple comparison, missing data)
- CLAUDE.md Phase 6 QC: per-round responsibility annotation (Claude / Dr. Editor / Dr. Statistician) with CRITICAL vs RECOMMENDED marking
- CLAUDE.md Phase 3→4 Completion Criteria: expanded to list all 9 `draft_plan.md` required items
- `docs/revision_guide.md`: new "QC Re-run for Revision" section with per-round re-run checklist and pre-submission checklist
- `docs/evidence_guide.md`: Search Log query examples updated to actual PubMed syntax (field tags `[tiab]`/`[MeSH]`, boolean AND/OR/NOT, quoted phrases)

### v0.5.2 (2026-04-15)

- Fixed cross-file inconsistencies across all documentation
- Updated figure format workflow: PNG for drafts (300 DPI), TIFF with LZW compression for final submission (600+ DPI), PPT/vector as options
- Updated `save_figure()` template: `draft=True` (PNG) / `final=True` (TIFF LZW) parameter split
- Added `review/reviewer_comments_REV{N}.md` to CLAUDE.md revision structure and File Roles table
- Fixed `analysis_plan.md` placeholder from `[FROM CLAUDE.md]` to user-friendly `[연구 설계 입력]`
- Aligned `revision_guide.md` file structure with CLAUDE.md (R1→REV1 naming convention)
- Added Round 4 template to `qc_guide.md` QC log and Final Sign-off
- Updated `statistical_analysis_guide.md` figure output format to include TIFF
- Updated `checklist_guide.md` figure submission requirements (TIFF LZW 600+ DPI)

### v0.5.1 (2026-04-15)

- Added Analysis Plan Mandatory (Critical Rule #7) — `analysis_plan.md` must be created and approved before running any statistical analysis
  - Per-paper analysis plans for multi-paper projects (`data/paper{N}_xxx/analysis_plan.md`)
  - Required contents: research questions, inclusion/exclusion criteria, variable definitions, test selection rationale, significance level
- Added Draft Plan Mandatory (Critical Rule #8) — `drafts/draft_plan.md` must be created and approved before drafting any sections
  - Required contents: key message, tone/voice, essential references, evidence gaps, table/figure plan, introduction/discussion outlines, limitation points
  - Per-paper draft plans for multi-paper projects
- Added Model Selection by Phase (Critical Rule #9) — cost-efficient model guidance
  - Opus recommended: Analysis Plan, Draft Plan, Revision (strategic phases)
  - Sonnet default with Opus optional: Drafting, Style Polish, QC (plan-guided execution)
  - Plan Mode (`/plan`) recommended for Draft Plan creation
- Workflow phases renumbered (7 → 8 phases): added Phase 3 (Draft Plan) between Analysis and Drafting
- Updated Phase Completion Criteria with draft_plan.md approval gate

### v0.5.0 (2026-04-14)

- Enhanced QC Round 2 (Reference Verification) with 4 new sub-checks:
  - 2.5 Placeholder Reference Detection — detect fake/temporary citations ([ref1], [TBD], [X], etc.)
  - 2.6 Order of Appearance Check — verify citation numbering follows Vancouver style order
  - 2.7 Reference Format Consistency — check bibliographic style uniformity across all references
  - 2.8 Citation Distribution Check — section-wise citation balance, self-citation rate, recency
- Strengthened Reference List Integrity (2.4) — added number continuity and duplicate number checks
- Updated QC Log template with Round 2 enhanced sections
- Added File Versioning rules (Critical Rule #5) — date-based default (`_YYMMDD`), `_v1`, `_REV1`, `_FINAL`
- Added Multi-Paper Organization (Critical Rule #6) — per-paper subfolders for data, results, drafts, output, review
- Added Multi-Paper Project structure diagram (shared docs/knowledge/scripts, separate per-paper folders)
- Added Revision folder structure — `drafts/revision/REV{N}/`, `output/revision/REV{N}/`
- Added Phase 7 (Revision) to Recommended Workflow with QC re-run requirement
- Updated Phase Completion Criteria with Submit → Revision path
- Updated File Roles table with revision folder entries

### v0.4.0 (2026-04-09)

- Added `docs/revision_guide.md` - Reviewer response and revision guide
- Added `docs/figure_guide.md` - Publication-quality figure generation guide
- Added `drafts/00_cover_letter.md` - Concise cover letter template
- Updated CLAUDE.md: project structure, file roles, Quick Commands for revision and figures
- Removed Spine GraphRAG project-specific references from project structure

### v0.3.0 (2026-03-09)

- Major rewrite of `docs/statistical_analysis_guide.md` (v0.2.1 → v0.3.0)
  - Statistical Parsimony, Analysis Hierarchy, Clinical Significance, Subgroup Analysis, Sensitivity Analysis
  - Methods Statistical Section Checklist (10 mandatory items per ICMJE/SAMPL)
- Updated `docs/writing_guide.md`, `docs/expert_roles.md`, `docs/qc_guide.md` for statistical consistency

### v0.2.5 (2026-03-09)

- Added `scripts/search_pubmed.py` - PubMed search tool using NCBI E-utilities API (no MCP, no external packages)
- Added slash commands: `/search-evidence [query]`, `/import-doi [doi]`

### v0.2.4 (2026-03-04)

- Added `.gitattributes` for LF line ending normalization
- Added `.gitignore` rules for `.DS_Store`, local settings, IDE config

### v0.2.3 (2026-02-15)

- Added `docs/docx_guide.md` for DOCX conversion rules
- Date-suffixed output files, separate title page and table DOCX files

### v0.2.2 (2026-02-10)

- Separated evidence guide from evidence registry
- Added `docs/evidence_guide.md` with detailed summarization instructions

### v0.2.1 (2026-02-07)

- Various structural fixes and template improvements

### v0.2 (2026-02-03)

- Added Statistical Analysis Guide
- Added Table/Figure/Results redundancy prevention rules

### v0.1 (Initial)

- Basic project structure
- Writing guide, expert roles, checklists, QC guide
