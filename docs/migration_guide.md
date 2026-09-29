# Migrating a copied template folder to the installed engine (v1.0.0)

Optional. A copied template folder keeps working as it is (Track A). Move a paper to the installed engine (Track B) when you want one engine for many papers and one-command updates. Nothing below deletes files.

1. **Back up** the paper folder. List local edits to engine files (`scripts/`, `harness/`, `docs/`, `.claude/`, `WORKFLOW.md`): `git status` / `git diff`, or compare with the template release you copied.
2. **Install** the CLI and the agent adapters from the same release:
   ```sh
   uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z
   manuwright doctor
   manuwright agents install --dry-run   # review, then run without --dry-run
   ```
3. **Manifest.** Create `project.json` (copy `docs/project.example.json` or run `manuwright init` in an empty folder and copy it over). List your real artifacts, tables, plans and records. Optionally pin the engine: `"engine": ">=1.8,<1.9"`.
4. **One set of hooks.** In `.claude/settings.json`, remove the entries that run `scripts/hooks/...` only after the plugin is installed, so hooks do not fire twice. (While they stay, plugin hooks detect them and stay silent.) Keep your own instructions in `CLAUDE.md`/`AGENTS.md`; add the rules from `docs/agent_bootstrap.md` if they are missing.
5. **Prove enforcement.** In a new agent session, ask it to write `drafts/04_methods.md` in a copy of the folder without an approved plan. The write must be blocked. Then run `manuwright verify --project project.json --profile draft` (or the profile you need).
6. **Reviews.** Semantic review and human signoff are bound to the engine files. If the installed engine differs from the copied one, re-review is required. This is intended.
7. **Keep** `data/`, `output/`, `profile/`, `Style/` and all project files. Deleting the copied engine files is optional and never required; archive them only after steps 5-6 pass.

Rollback: uninstall the adapters (`claude plugin uninstall manuwright`, `codex plugin remove manuwright`, ...), restore the hook entries, and keep using the copied engine.

Updating a copied template (Track A): a ZIP or "Use this template" copy has no upstream. Replace the public engine files (`scripts/`, `harness/`, `docs/`, `.claude/commands/`, `.claude/settings.json`, `WORKFLOW.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `Style/terminology.md`) from the new release after diffing your local edits. A real `git clone` can `git pull`.
