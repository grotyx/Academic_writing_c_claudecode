#!/bin/sh
# Portable hook launcher (POSIX sh). Claude Code hook commands in
# .claude/settings.json go through this so one settings file works everywhere:
# Windows has the `py` launcher (and `sh` via Git Bash, which Claude Code
# requires there); macOS/Linux have `python3` but no `py`. Without this shim
# every hook exits 127 on macOS/Linux and enforcement is silently OFF.
command -v py >/dev/null 2>&1 && exec py "$@"
command -v python3 >/dev/null 2>&1 && exec python3 "$@"
echo "WARNING: no py/python3 found; workflow hooks (plan-first gates) are OFF." >&2
exit 1
