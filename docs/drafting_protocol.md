# Drafting Protocol

> Mandatory workflow for drafting manuscript sections. This protocol prevents unsupported claims, terminology drift, and generic LLM prose.

---

## Required Inputs Before Drafting

Before drafting any section, check these files:

| Input | Purpose |
|---|---|
| `drafts/draft_plan.md` | Key message, tone, table/figure plan, claim-to-citation mapping |
| `data/analysis_plan.md` | Research question, endpoints, statistical methods |
| `results/` and `drafts/table_*.md` | Numerical results and table references |
| `knowledge/evidence.md` | Verified citation support |
| `Style/terminology.md` | Preferred and forbidden terminology |
| `Style/style_guide.md` and relevant `Style/*/*.md` anchors | House style, team voice, argument patterns |
| `docs/section_templates.md` | Section-specific structure and sentence patterns |
| `docs/writing_guide.md` | General academic writing rules |

Do not draft if `drafts/draft_plan.md` is absent or incomplete.

---

## Drafting Sequence

### Step 1. Paragraph-Level Outline

Create a paragraph-level outline before writing prose.

Each paragraph must include:
- Paragraph function
- Source of content: evidence number, table, figure, analysis plan, or style anchor
- Allowed claims
- Forbidden content

Example:

```markdown
Paragraph 2: Evidence gap
- Function: explain limitation of prior studies
- Source: draft_plan claim 4; evidence [7], [9]
- Allowed claim: comparative evidence remains limited for [population]
- Forbidden: claim superiority, mention current study results
```

### Step 2. Evidence-Bound Draft

Convert the outline to prose using only mapped evidence and approved results.

Rules:
- Introduction claims must map to `knowledge/evidence.md` or approved style anchors.
- Methods must match `data/analysis_plan.md`.
- Results must match `drafts/table_*.md` and `results/`.
- Discussion interpretation must be grounded in the actual Results.
- No new citations, numbers, endpoints, or analyses may be invented during drafting.

### Step 3. Section Template Pass

Apply `docs/section_templates.md`.

Rules:
- Use the section's paragraph functions.
- Use sentence patterns as patterns, not copied boilerplate.
- Follow section-specific forbidden content rules.

### Step 4. Terminology Pass

Apply `Style/terminology.md`.

Rules:
- Replace forbidden terms with preferred terms.
- Define abbreviations once in the main text.
- Do not mix synonyms for the same concept.
- If the target journal requires a different term, document the exception in `drafts/draft_plan.md`.

### Step 5. Style Anchor Pass

Apply relevant files under `Style/own/`, `Style/landmark/`, and `Style/target_journal/`.

Rules:
- Use own anchors for team voice and Methods consistency.
- Use landmark anchors for argument structure and framing.
- Use target-journal anchors for house style and reporting density.
- Do not copy full sentences or paragraphs from source papers.

### Step 6. Lint and QC Pass

Run the manuscript lint script:

```bash
py scripts/lint_manuscript.py drafts --quiet
```

Address high-priority findings before considering the section complete.

### Step 7. Verification Gate (자율 루프)

섹션 작성이 끝나면 다음 단계로 넘어가기 전에 검증 게이트를 통과해야 한다.
상세: `docs/verification_protocol.md`.

1. 네 Verifier 서브에이전트를 투입한다 (모델: Opus 기본):
   - **Constraint** — draft_plan·analysis_plan·사용자 제약 준수
   - **Citation** — `[EVID:id]` 인용이 evidence.md로 지지되는지 (방향·대상·비교군·결과 일치)
   - **Data** — 모든 결과 수치가 `results/*.csv`로 추적되는지
   - **Logic** — 섹션 간 논리 흐름·중복 (Results 해석이 Discussion으로 새지 않는지 등)
2. 모두 PASS → `review/gates/phase_04_draft.GATE.md`에 `status: PASS` 기록 → 다음 섹션.
3. FAIL → 지적사항을 수정하고 재검증. 최대 2회(N=2), 이후 사용자에게 에스컬레이션.

게이트 PASS가 원장에 기록되기 전에는 다음 섹션을 시작하지 않는다.

---

## Section-Specific Guardrails

| Section | Must Use | Must Not Use |
|---|---|---|
| Introduction | Background evidence, gap, purpose | Current study results or interpretation |
| Methods | Approved design, endpoints, analyses | Results, post hoc methods not in analysis plan |
| Results | Tables, figures, analysis outputs | Interpretation, clinical implications, causal claims |
| Discussion | Principal findings, comparison, implications, limitations | New results, unsupported claims, overstatement |
| Conclusion | Brief take-home message | New claims, exact numbers, overgeneralization |

---

## Completion Checklist

- [ ] Paragraph outline was created before prose.
- [ ] Every factual claim has an evidence/table/analysis-plan source.
- [ ] No unsupported citation or placeholder remains.
- [ ] Terminology follows `Style/terminology.md`.
- [ ] Section follows `docs/section_templates.md`.
- [ ] Style anchors were applied without copying source text.
- [ ] `scripts/lint_manuscript.py` was run and findings were addressed or documented.
- [ ] Verification gate (Constraint/Citation/Data/Logic) passed, recorded in `review/gates/`, and passed `scripts/check_gate.py`.

---

## Machine Gate Sequence

Use this sequence after each produce step:

1. Run deterministic helpers first: `check_citations.py`, `check_numbers.py`, and for revision `check_revision_claims.py`.
2. Run LLM semantic verifiers using `docs/verifier_prompt_templates.md`.
3. Record the result in `review/gates/phase_NN_<name>.GATE.md`.
4. Confirm the ledger before proceeding:

```powershell
py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md --verify-hash results=results\table2_outcomes.csv
```
