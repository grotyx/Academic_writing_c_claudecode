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
import shutil
import subprocess
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


def choose(kind, sets, current, known, prices, ask):
    """Numbered menu: a set, none, keep, or own ids. Returns the chosen list (None = keep)."""
    names = list(sets)
    print(f'  Recommended {kind} sets (updated {UPDATED}):')
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
    print(f'OpenRouter sets (updated {UPDATED}; ~cost of one review: 25k tokens in, 4k out)')
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
