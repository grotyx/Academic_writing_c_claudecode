# Style Transformation Protocol

> Turn a rough draft into bound academic/journal style — reliably, without repeating the
> same style note. Triggered by `/style-pass`, or automatically when you ask to "make it
> academic / 학술적으로 바꿔줘" (the `scripts/hooks/style_intent.py` UserPromptSubmit hook
> injects this protocol). Used in Phase 5 (Style Polish) and Phase 8 (revision rewrites).

## Why this exists

"Academic style" is abstract, so it gets reinterpreted every time, and the 28 `Style/`
anchors never fit in active context. This protocol fixes that by (1) binding ONE exemplar
into a compact **Style Spec** that loads every session, (2) transforming **section by
section** grounded on that spec, and (3) verifying each section with an independent
**Style-Conformance Verifier** (auto-fix loop). The deterministic word/notation layer is
handled by `scripts/hooks/lint_on_edit.py`.

## Inputs (source of truth)

- `drafts/style_spec.md` — the bound Style Spec (multi-paper: `drafts/paper{N}_xxx/style_spec.md`).
- The bound exemplar anchor: `Style/own/<id>.md` or `Style/target_journal/<id>.md`.
- `docs/writing_guide.md` (section rules + Concision Pass) + `docs/section_templates.md`.
- `Style/terminology.md`.

No outside style preferences. If there is no Style Spec, create one first (Step 0).

## Procedure

### Step 0 — Bind an exemplar (once per project)
If `drafts/style_spec.md` is absent: ask (`AskUserQuestion`) which anchor to bind — recommend
the closest `Style/own/` paper or the `Style/target_journal/` paper. Copy
`docs/style_spec_template.md` → `drafts/style_spec.md` and fill the targets from that anchor
(+ `profile/journals.md` for reference format). Get the author's confirmation.

### Step 1 — Scope
Confirm with the author what to transform (whole draft vs specific sections). Do NOT silently
rewrite everything.

### Step 2 — Transform, section by section
For EACH section, in drafting order (Methods → Results → Introduction → Discussion →
Conclusion → Abstract → Title):
1. Load the Style Spec + the matching section of the bound exemplar + the `writing_guide`
   section rules.
2. Rewrite the section toward the spec: structure/flow, sentence length, hedging, claim
   strength, reference format, voice/tense. Keep claims and numbers grounded — do not invent.

### Step 3 — Verify each section (auto-fix loop)
First the **measurable layer**: `py scripts/check_style.py check <section> --spec drafts/style_spec.md`
flags metric deviations (word count, mean sentence length, paragraphs, citation density) from
the Spec targets. Then the **Style-Conformance Verifier** (`docs/verifier_prompt_templates.md`)
on the section against the Style Spec + exemplar for the qualitative layer (flow, claim
strength, "Do Not Imitate"). On FAIL, fix and re-verify — **max 2 loops**, then escalate to
the author. The `lint_on_edit.py` hook also surfaces terminology + style-metric residue
automatically after each edit when a Style Spec exists.

### Step 4 — Record
Record a `style` check PASS in `review/gates/phase_05_style.GATE.md` (template
`review/gates/_TEMPLATE.GATE.md`); verify with `scripts/check_gate.py` (`--verify-hash`).

## Guardrails

- Grounding is unchanged: never invent citations or numbers to fit a sentence pattern
  (CLAUDE.md Rule 1 + STOP signals). Style is not a license to overclaim — the Spec's
  claim-strength calibration is binding.
- Over-compression caution: apply the `writing_guide` Concision Pass, but do not delete
  clinical qualifiers, safety caveats, or grounded numbers to hit a length target.
- The auto-trigger is advisory and fails open; it never blocks your prompt.
