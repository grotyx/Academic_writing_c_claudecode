# Distribution Plan: Two-Track Install (v0.5.0, 2026-09-30; phases 1-2 done in v1.7.6-v1.7.7)

Status: proposal, not implemented. Target release: v1.8.0.
v0.2.0 folds in a Codex (gpt-6-astra) design review and a survey of comparable projects (section 9).

## 1. Goal

One repository, two ways to use it. Both run the same engine code and the same rules.

| Track | Who | Get it | Update |
|---|---|---|---|
| **A. Template (no install)** | Copy a folder and work in it (today's users) | `git clone` / GitHub template / ZIP | Documented public-file update set (section 7); `git pull` only for real clones |
| **B. Installed** | Many papers, one engine | `uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z` + Claude Code plugin from the same tag | `uv tool install --force ...@<new tag>` + `/plugin marketplace update` |

Track A behavior must not change. Track B adds packaging on top. No second editable copy of any checker.

Claude Code and Codex work together in both tracks: same engine, same rules, same project files (section 5).

## 2. Path model (changed from v0.1)

v0.1 proposed a global `PROJECT_ROOT` (manifest, env, then cwd). Rejected: it silently changes legacy defaults. Example: `python /template/scripts/check_citations.py ...` run from another folder today reads `/template/knowledge/evidence.md`; a cwd fallback would read a different registry.

New rule:

- **Engine root** stays `Path(__file__)`-based. It locates code and shipped assets only. `harness/project.py:9` already works this way.
- **Project paths are explicit.** The manifest (`--project project.json`) is the authority; its parent resolves all paper files (already true in `harness/`). The installed wrapper resolves the project once at entry and passes explicit paths (`--evidence`, `--results`, ...) into the existing checker functions.
- **Legacy script defaults stay as they are** when no project is selected. No global `chdir`, no mutated module globals, no environment variable that redirects a Track A command.
- **Hooks** keep resolving the edited file from the event `cwd`; plans stay adjacent to the edited section (multi-paper safe). `CLAUDE_PROJECT_DIR` is used only inside hooks.
- `inside()` containment checks (`harness/results.py:15`) are preserved.

Full per-file inventory of root-sensitive code: Codex review section 4 (kept in the PR description of phase 1).

## 3. Layout

```
repo/
├── pyproject.toml            # package build: harness + scripts + allowlisted assets; requires-python >=3.10
├── harness/                  # engine API (unchanged); version stays in harness/__init__.py
├── scripts/                  # unchanged names; Track A keeps `python scripts/x.py`
├── .claude-plugin/
│   ├── plugin.json           # Claude Code plugin manifest
│   └── marketplace.json      # this repo is its own one-plugin marketplace
├── skills/                   # few short entry skills that load canonical docs (no prose splitting)
├── hooks/hooks.json          # plugin hooks, quoted ${CLAUDE_PLUGIN_ROOT}
├── .claude/, WORKFLOW.md, CLAUDE.md, AGENTS.md, GEMINI.md, docs/   # Track A, unchanged role
```

- Console script `paperflow` maps to `harness.__main__` plus an explicit dispatch table for the supported standalone scripts (`check citations|numbers|gate|...`, `search`, `evidence-table`, `extract-claims`, `critical-review`), preserving flags and exit codes.
- Wheel content is an allowlist: code, `Style/terminology.md`, `scripts/critical_prompts/`, `scripts/critical_models.txt`, `WORKFLOW.md`, runtime `docs/` (protocols, templates, verifier prompts), `docs/project.example.json`. Never PDFs, `profile/`, private Style anchors, drafts, data.
- Sibling-import scripts must still run from a raw checkout with no install and no `PYTHONPATH`.

## 4. Track B details

- **CLI required for the plugin (v1.8.0).** Plugin commands and hooks call `paperflow`. The plugin checks `paperflow --version` against its own version and fails loudly on mismatch. No silent fallback to a different engine.
- **Commands:** `paperflow doctor | init | status | verify | packet | build | record-approval | check <name> | rules [phase] | hook <name>`. `paperflow verify --project` (manifest profiles) stays distinct from the legacy artifact-based `/verify` (`scripts/verify_all.py`).
- **`paperflow init <folder>`** builds a starter from existing templates (`docs/project.example.json`, plan templates), creates `data/ drafts/ knowledge/ results/ review/`, refuses to overwrite, leaves plans unapproved and creates no review receipts. A fresh init is expected to report incomplete setup.
- **Freshness:** snapshot keeps logical `@engine/...` names, so a byte-identical engine installed elsewhere does not stale reviews; real content changes do. New runtime files (dispatch table, packaged docs that affect verification) enter the snapshot.
- **Always-on rules stay always-on.** The mandatory contract remains in the project bootstrap (`CLAUDE.md` / `AGENTS.md`) and the SessionStart hook. Phase detail loads on demand from skills or `paperflow rules <phase>`.
- **Updates are pinned:** CLI and plugin are released from the same git tag.

## 5. Supported agents and updates

Target agents: Claude Code, Codex, Antigravity CLI (`agy`, Gemini), opencode, Muse. All share one engine (`paperflow`) and one project folder. One `skills/` source (SKILL.md format) plus thin per-agent adapters.

| Agent | Mandatory rules | Install adapter (Track B) | Update | Hook enforcement |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` + SessionStart hook | `/plugin marketplace add grotyx/...`, `/plugin install paperflow@...` | marketplace auto-update toggle, or `/plugin marketplace update`; users move only when plugin `version` changes | yes (PreToolUse) |
| Codex | `AGENTS.md` | `codex plugin marketplace add <git url>`, `codex plugin add ...` (or `.agents/skills`) | `codex plugin marketplace upgrade` | no; `paperflow verify` gates |
| Antigravity (`agy`) | `GEMINI.md` / `AGENTS.md` | `agy plugin install paperflow@<marketplace>` (can also `agy plugin import` from Claude) | reinstall from marketplace | check at implementation |
| opencode | `AGENTS.md` | skills in `~/.config/opencode/skills` or project `.opencode/`; plugin via `opencode.json` | re-copy skills / plugin version bump | check at implementation |
| Muse | `AGENTS.md` | `muse skills install <path>` or `muse skills import --from claude` | `muse skills update <id>` | check at implementation |

`paperflow agents install|update [--only claude,codex,agy,opencode,muse]` runs each agent's native command above (dry-run first). No custom installer beyond calling native commands.

### Update policy

- **Check automatically, apply explicitly.** The engine is bound into review hashes; changing it mid-paper stales semantic and human-signoff receipts. So nothing upgrades silently.
- SessionStart hook / `paperflow doctor` checks the latest release tag at most once a day (skippable offline, `PAPERFLOW_NO_UPDATE_CHECK=1`) and prints: `paperflow 1.8.2 available: run paperflow update`.
- `paperflow update` = `uv tool install --force git+...@<latest tag>` + `paperflow agents update` + prints which projects' reviews will go stale.
- Optional per-project pin: `"engine": ">=1.8,<1.9"` in `project.json`; `verify` refuses a mismatched engine, so a paper under submission stays on one engine.
- **Auto-update (opt-in):** `paperflow config set auto-update on`. At session start (at most once a day) it runs `paperflow update` by itself, but only when every rule below holds; otherwise it falls back to the notice.
  - The new release stays inside the current project's `engine` pin (default: same minor, patch-only).
  - No project on this machine has a fresh semantic review or human signoff that the update would stale (checked via each known project's last `review/state.json`); submissions in progress are never broken silently.
  - The update is logged to `~/.paperflow/update.log` and printed in the session with the previous version, so `paperflow update --to <old tag>` can roll back.
  - Agent adapters (plugin/skills) are updated in the same run, so CLI and adapters never drift.
- Claude plugin auto-update can be turned on by the user; it only changes adapters (skills/hooks), and the version check (section 4) blocks a plugin/CLI mismatch until `paperflow update` runs.

## 6. Phases (reordered)

| # | Work | Done when |
|---|---|---|
| 1 ✅ | Compatibility contract + tests (`tests/test_compat_contract.py`, v1.7.6): freeze legacy CLI semantics; tests run scripts from repo root, a nested folder and an unrelated cwd with no install; conflicting env var; manifest outside repo; two projects in one process; hooks with event cwd != engine cwd, spaces/Unicode paths | Suite green on current code (tests describe today's behavior) |
| 2 ✅ | (v1.7.7) `pyproject.toml`, `paperflow` entry + dispatch table, asset allowlist, snapshot coverage; CI builds the wheel and runs it outside the checkout | Installed and source tests both green; docs/version bumped in same PR |
| 3 | `paperflow init`, `paperflow rules`, bootstrap snippets for CLAUDE/AGENTS/GEMINI (preserving local text) | Fresh init reports incomplete; synthetic complete project passes |
| 4 | Claude plugin: manifest, marketplace, hooks, a few entry skills; version-match check; duplicate-hook guard for migrating folders | Plugin commands work on a paper outside the repo |
| 5 | README for both tracks, opt-in migration guide, tag v1.8.0 | Tag cut only after installed + source tests pass |

Dropped from v1.8.0: WORKFLOW-to-skills prose generator, blind command-text rewriting, CLI-vs-bundled-engine fallback, custom updater, PyPI publishing, automated deletion of copied engine files.

## 7. Migration (opt-in, non-destructive)

1. Back up the paper folder; note local edits to engine files.
2. Install CLI + plugin from the same tag. Create or validate `project.json`.
3. Remove only duplicate hook registrations from `.claude/settings.json` so local and plugin hooks do not both fire. Keep user instructions.
4. Exercise real events: a plan-less section write must be blocked; style hook must fire. Then re-run the needed profile.
5. Existing semantic and human-signoff receipts may go stale if engine content differs. Re-review is required.
6. Keep `data/ output/ profile/ Style/` and all project files. Deleting the copied engine is optional, never required.

Track A update: a ZIP/template copy has no upstream. Publish an explicit list of public engine files to replace, and tell users to diff local edits first.

## 8. Risks

- Interpreter skew: uv-managed CLI Python vs bare `python3`/`py` in hooks. Hooks call `paperflow hook ...` in Track B; `run.sh` keeps `py` then `python3` for Track A.
- CLI/plugin version skew: same tag, explicit version check.
- Resource completeness: CI asserts every path a command/skill references exists in the installed package.
- Private data: sdist/wheel built from an allowlist; Track B keeps papers out of the public template repo.
- Offline: both tracks run offline once installed; installation itself needs network (or a pre-built wheel).
- Plugin command names get a plugin prefix; keep logical names identical and document the qualified form.

## 9. Prior art (checked 2026-09-29)

| Project | Install | Update | Drift control |
|---|---|---|---|
| GitHub Spec Kit (Python CLI + agent skills) | `uv tool install specify-cli --from git+...@vX.Y.Z`; `uvx` for no persistent install | `uv tool install --force` to new tag; separate `integration upgrade` refreshes project files | Install manifest detects local edits; CLI upgrade and instruction refresh are separate steps |
| Fission-AI OpenSpec (Node CLI + skills) | `npm i -g`, then `openspec init` | upgrade package, then `openspec update` per project | Skills/commands generated from structured templates in code |
| caveman (installed here) | one repo: Claude plugin marketplace, Gemini extension, `npx skills add` for Codex/Cursor, `install.sh` for no-plugin users | per agent native update | shared `skills/` source, per-agent adapters |
| ponytail (installed here) | same pattern: `.claude-plugin/`, `AGENTS.md`, `gemini-extension.json`, `skills/` | per agent native update | one `skills/` folder, thin per-agent manifests |
| Claude Code plugins (official docs) | `/plugin marketplace add owner/repo`, `/plugin install name@marketplace` | `/plugin marketplace update`; users move only when plugin `version` changes | pin refs; bump version on every release |
| Codex | skills in `.agents/skills` (repo) or `~/.agents/skills`; `AGENTS.md` for startup rules; `codex plugin` for bundles | repo pull or plugin update | `AGENTS.md` for mandatory rules, skills for on-demand detail |

Lesson used here: one canonical source, thin per-agent adapters, CLI upgrade and project-file refresh as separate explicit steps, and releases pinned to one tag.
