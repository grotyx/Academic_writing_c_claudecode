"""Recommended reviewer model sets for OpenRouter and opencode, checked against the live lists.

Sets name the newest model of each open-weight family (GLM, Kimi, MiniMax, DeepSeek, Qwen, Xiaomi MiMo,
Meituan LongCat) at a sensible price. Free and "contributor" tiers are left out on purpose: they may keep
prompts for training, and a review sends the unpublished manuscript.
They ship with each release (auto-update keeps them current); `manuwright models` shows which are
still offered and what one review roughly costs. Typed model ids are checked the same way, with a
closest-match suggestion, but never blocked: the lists can be unreachable offline.
"""
from __future__ import annotations

import difflib
import json
import os
import sys
import shutil
import subprocess
import urllib.error
import urllib.request

UPDATED = '2026-10-01'
OPENROUTER_SETS = {
    'balanced': ('Recommended: newest mid-price model of each family', [
        'z-ai/glm-5.3', 'moonshotai/kimi-k3', 'minimax/minimax-m3', 'deepseek/deepseek-v4-pro-0813',
        'qwen/qwen3.7-plus', 'xiaomi/mimo-v2.6-pro']),
    'budget': ('Lowest cost, fast flash models', [
        'z-ai/glm-5.3-flash', 'deepseek/deepseek-v4.1-flash', 'qwen/qwen3.8-flash', 'xiaomi/mimo-v2.6-flash',
        'meituan/longcat-2.0']),
    'strong': ('Strongest of each family (several times the cost)', [
        'z-ai/glm-5.3-prime', 'moonshotai/kimi-k3', 'deepseek/deepseek-v4-pro-0813', 'qwen/qwen3.8-max-0902']),
}
OPENCODE_SETS = {
    'go': ('opencode Go subscription: newest model of each family', [
        'opencode-go/glm-5.3', 'opencode-go/kimi-k3', 'opencode-go/minimax-m3', 'opencode-go/deepseek-v4-pro',
        'opencode-go/qwen3.8-max', 'opencode-go/mimo-v2.6-pro']),
    'go-budget': ('opencode Go subscription: flash models', [
        'opencode-go/glm-5.3-flash', 'opencode-go/deepseek-v4.1-flash', 'opencode-go/qwen3.8-flash',
        'opencode-go/mimo-v2.6-flash', 'opencode-go/longcat-2.0']),
}
WRITERS = ['anthropic/claude-opus-5.5', 'anthropic/claude-sonnet-5.5', 'anthropic/claude-fable-5.1',
           'openai/gpt-6-astra', 'openai/gpt-6.1-sol', 'google/gemini-3.8-flash']
AGENTS = ['claude', 'codex', 'muse', 'agy']
# Agent CLIs run on the plan you are signed in with; OpenRouter is billed per call.
AGENT_LABELS = {'claude': 'Claude Code (subscription)', 'codex': 'Codex (subscription)',
                'muse': 'Muse Code (subscription)', 'agy': 'Antigravity / Gemini (subscription)'}
BILLING = {'OpenRouter': 'pay per use with your OpenRouter key', 'opencode': 'opencode Go subscription'}
# One manuscript review: about 25k tokens in, 4k out.
REVIEW_TOKENS = (25_000, 4_000)


def openrouter_prices():
    """{model id: (input $/token, output $/token)}; {} when OpenRouter is unreachable."""
    try:
        with urllib.request.urlopen('https://openrouter.ai/api/v1/models', timeout=10) as response:
            data = json.load(response)['data']
        return {m['id']: (float(m['pricing']['prompt']), float(m['pricing']['completion'])) for m in data}
    except (OSError, ValueError, KeyError):
        return {}


def opencode_models():
    """Model ids opencode can use; empty when opencode is missing or slow."""
    if not shutil.which('opencode'):
        return set()
    try:  # detached from the terminal (see obsidian.DETACHED)
        done = subprocess.run(['opencode', 'models'], capture_output=True, text=True, timeout=30,
                              stdin=subprocess.DEVNULL, start_new_session=True)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return {line.strip() for line in done.stdout.splitlines() if '/' in line}


def key_works(key):
    """True/False from OpenRouter's key endpoint; None when it cannot be reached."""
    request = urllib.request.Request('https://openrouter.ai/api/v1/key', headers={'Authorization': f'Bearer {key}'})
    try:
        with urllib.request.urlopen(request, timeout=10):
            return True
    except urllib.error.HTTPError as error:
        return False if error.code in (401, 403) else None
    except OSError:
        return None


def review_cost(price):
    return price[0] * REVIEW_TOKENS[0] + price[1] * REVIEW_TOKENS[1]


def describe(models, known, prices=None):
    """One line per model: availability, and the rough cost of one review when priced."""
    lines = []
    for model in models:
        mark = '?' if not known else ('ok' if model in known else 'not offered now')
        cost = f'  ~${review_cost(prices[model]):.3f}/review' if prices and model in prices else ''
        lines.append(f'      {model}  [{mark}]{cost}')
    return lines


def check(models, known):
    """Warnings for ids missing from a non-empty live list, with the closest match."""
    out = []
    for model in models:
        if known and model not in known:
            close = difflib.get_close_matches(model, sorted(known), n=1, cutoff=0.6)
            out.append(f'  "{model}" is not in the current list' + (f'; did you mean "{close[0]}"?' if close else '.'))
    return out


# --- selection menu ---------------------------------------------------------
UP, DOWN, SPACE, ENTER, ESC = 'up', 'down', ' ', 'enter', 'esc'


def read_keys():
    """Yield key names from a raw terminal (POSIX). The caller restores the terminal."""
    import select
    fd = sys.stdin.fileno()
    while True:
        ch = os.read(fd, 1).decode(errors='ignore')
        if ch == '\x1b':
            seq = os.read(fd, 2).decode(errors='ignore') if select.select([fd], [], [], 0.05)[0] else ''
            yield {'[A': UP, '[B': DOWN}.get(seq, ESC)
        elif ch in ('\r', '\n'):
            yield ENTER
        elif ch == '\x03':
            raise KeyboardInterrupt
        else:
            yield ch


def can_menu():
    return os.name == 'posix' and sys.stdin.isatty() and sys.stdout.isatty()


def pick(title, options, selected, presets=None, single=False, keys=None):
    """Arrow-key menu. options: [(value, label)]. Space toggles (single: Enter picks), letters apply
    presets {key: (name, values)}, a/n select all/none, Esc keeps the current choice (returns None)."""
    presets = presets or {}
    chosen = {v for v, _ in options if v in selected}
    row = next((i for i, (v, _) in enumerate(options) if v in chosen), 0)
    help_line = ('↑/↓ move · Enter choose · Esc keep current' if single else
                 '↑/↓ move · Space select · Enter done · a all · n none · Esc keep current'
                 + ''.join(f' · {k} {name}' for k, (name, _) in presets.items()))
    drawn = 0

    def draw():
        nonlocal drawn
        if drawn:
            sys.stdout.write(f'\x1b[{drawn}F\x1b[J')
        lines = [f'  {title}', f'  {help_line}']
        for i, (value, label) in enumerate(options):
            box = '' if single else ('[x] ' if value in chosen else '[ ] ')
            lines.append(f"  {'>' if i == row else ' '} {box}{label}")
        sys.stdout.write('\n'.join(lines) + '\n')
        sys.stdout.flush()
        drawn = len(lines)

    source = keys
    saved = None
    if source is None:
        import termios
        import tty
        saved = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        source = read_keys()
    try:
        draw()
        for key in source:
            if key in (UP, 'k'):
                row = (row - 1) % len(options)
            elif key in (DOWN, 'j'):
                row = (row + 1) % len(options)
            elif key == ESC or key == 'q':
                return None
            elif key == ENTER:
                return [options[row][0]] if single else [v for v, _ in options if v in chosen]
            elif single:
                continue
            elif key == SPACE:
                chosen ^= {options[row][0]}
            elif key == 'a':
                chosen = {v for v, _ in options}
            elif key == 'n':
                chosen = set()
            elif key in presets:
                chosen = set(presets[key][1])
            draw()
        return None
    finally:
        if saved is not None:
            import termios
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved)


def model_options(sets, current, known, prices):
    """Every model in the sets (plus any current custom id), labelled with availability and cost."""
    values = list(dict.fromkeys([m for _, models in sets.values() for m in models] + list(current)))
    options = []
    for model in values:
        if known and model not in known:
            note = 'not offered now'
        elif prices and model in prices:
            note = f'~${review_cost(prices[model]):.3f}/review'
        else:
            note = ''
        options.append((model, f'{model:<36} {note}'.rstrip()))
    return options


def choose(kind, sets, current, known, prices, ask):
    """Pick models: an arrow-key checklist on a terminal, a numbered list otherwise. None = keep."""
    if can_menu() and ask is input:
        presets = {str(i): (name, models) for i, (name, (_, models)) in enumerate(sets.items(), 1)}
        return pick(f'{kind} reviewer models ({BILLING.get(kind, kind)}; sets updated {UPDATED}; '
                    f'number keys fill a recommended set)',
                    model_options(sets, current, known, prices), set(current), presets)
    names = list(sets)
    print(f'  Recommended {kind} sets ({BILLING.get(kind, kind)}; updated {UPDATED}):')
    for i, name in enumerate(names, 1):
        print(f'   {i}. {name}: {sets[name][0]}')
        print('\n'.join(describe(sets[name][1], known, prices)))
    print('   0. none')
    while True:
        answer = ask(f'  Pick 0-{len(names)}, or type model ids (comma-separated) '
                     f'[{",".join(current) or "none"}]: ').strip()
        if not answer:
            return None
        if answer.isdigit():
            if int(answer) <= len(names):
                return [] if answer == '0' else list(sets[names[int(answer) - 1]][1])
            print('  not valid here; try again.')
            continue
        models = [m.strip() for m in answer.split(',') if m.strip()]
        warnings = check(models, known)
        if not warnings:
            return models
        print('\n'.join(warnings))
        if ask('  Use them anyway? [y/N]: ').strip().lower() in {'y', 'yes'}:
            return models


def main(args):
    """manuwright models: recommended sets with live availability and cost."""
    prices = openrouter_prices()
    print(f'OpenRouter sets (pay per use; updated {UPDATED}; ~cost of one review: 25k tokens in, 4k out)')
    for name, (about, models) in OPENROUTER_SETS.items():
        print(f'  {name}: {about}')
        print('\n'.join(describe(models, set(prices), prices)))
    known = opencode_models()
    print(f'\nopencode sets (opencode Go is a subscription; {"live list checked" if known else "opencode not found"})')
    for name, (about, models) in OPENCODE_SETS.items():
        print(f'  {name}: {about}')
        print('\n'.join(describe(models, known)))
    print('\nChoose one in `manuwright setup`, or set it directly:\n'
          '  manuwright config set review.openrouter-models z-ai/glm-5.3,moonshotai/kimi-k3\n'
          '  manuwright config set review.reviewers "codex, openrouter, opencode:opencode-go/glm-5.3"')
    return 0
