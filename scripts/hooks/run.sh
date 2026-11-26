#!/bin/sh
# Portable hook launcher (POSIX sh). Claude Code hook commands in
# .claude/settings.json go through this so one settings file works everywhere:
# Windows has the `py` launcher (and `sh` via Git Bash, which Claude Code
# requires there); macOS/Linux have `python3` but no `py`. Without this shim
# every hook exits 127 on macOS/Linux and enforcement is silently OFF.
# Windows (Git Bash): py first, since python3 there may be the Store stub. Elsewhere python3 first:
# a stray `py` on macOS/Linux (pyenv shims, other tools) is not the Python launcher.
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) command -v py >/dev/null 2>&1 && exec py "$@" ;;
esac
command -v python3 >/dev/null 2>&1 && exec python3 "$@"
command -v py >/dev/null 2>&1 && exec py "$@"
echo "WARNING: no py/python3 found; workflow hooks (plan-first gates) are OFF." >&2
exit 1
