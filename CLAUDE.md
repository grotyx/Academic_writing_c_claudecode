# Academic Paper Writing Project (v1.7.2)

@WORKFLOW.md

The line above imports `WORKFLOW.md` into every Claude Code session automatically. Read `WORKFLOW.md` in full before work. It is the authoritative shared workflow for every runtime. Research configuration and numbered rules, including Rule 12 documentation/version/git policy, are there.

Read `docs/harness_guide.md` for the common executable interface. Claude slash commands and `.claude/settings.json` hooks are convenience adapters; they do not replace explicit verification or authorize external provider transmission. On Windows the hook launcher requires a POSIX `sh` (for example Git Bash).

Run `python -m harness doctor` to inspect installed capabilities without sending data. Use a project manifest for verification and submission builds. Follow `AGENTS.md` for protected files and git hygiene.
