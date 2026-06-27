# Verification Protocol (검증 하네스) (v0.3.0)

> harness-engineering식 produce→verify→fix→re-verify 자동 루프 정의.
> 각 산출 단계 뒤에 검증 게이트를 두어 제약 무시·인용 환각·수치 조작을 차단한다.
> 검증은 **Verifier 서브에이전트 + 프로토콜 규칙**을 기본으로 수행하되, deterministic helper script가 있는 경우 먼저 실행한다.
> Phase 8 ghost-revision 검증은 `scripts/check_revision_claims.py`로 response-letter `[CHANGE]` claims를 revised manuscript 파일과 대조한다.
> Semantic checks that require LLM judgment must use `docs/verifier_prompt_templates.md`.

---

## 1. 핵심 개념 — Produce → Verify-Gate → Loop

모든 산출 단계(섹션 작성, claim 매핑, revision 응답) 뒤에 검증 게이트를 둔다.

```
[Produce] → [Verifier 서브에이전트] → PASS → [게이트 원장 기록] → 다음 단계
                     │
                    FAIL → [Fix] → re-verify (최대 2회) → 사용자 에스컬레이션
```

- 차단 장치: `review/gates/`의 게이트 원장에 해당 산출물 `status: PASS`가 없으면 다음 섹션/단계 진행 금지.
- 자율 루프: FAIL 시 지적사항을 고쳐 재검증. 최대 2회(N=2) 반복 후에도 FAIL이면 멈추고 사용자에게 보고.

---

## 2. Verifier 헌장

Draft 게이트는 네 개의 Verifier(Constraint / Citation / Data / Logic)를 투입한다. Revision 게이트는 Logic을 제외하고 Ghost-Revision(revision_claims) + Response-alignment를 더한다 — 즉 Constraint / Citation / Data / Revision-claims / Response-alignment. 모든 Verifier는 공통 규칙을 따른다:
- **외부지식 사용 금지.** 주어진 소스(소스 오브 트루스)와 산출물만으로 판정한다.
- **불확실하면 FAIL 기본값.** 지지 여부가 모호하면 PASS로 넘기지 않는다.
- **판정 결과를 구조화 출력**한다 (3.2 형식).

> **실행 순서 (Constraint 우선 + 병렬 검출):** 네 Verifier는 검출 단계에서 **병렬**로 돌린다(§3.1). 다만 **Constraint(명세 적합)를 1순위 관문으로 본다** — 섹션이 draft_plan의 scope·tone·forbidden content를 위반하면, Phase 5 문체 손질을 시작하기 전에 먼저 바로잡는다. 곧 폐기될 문장을 다듬는 낭비를 막기 위함이다. 두 개 이상이 FAIL이면 수정도 Constraint부터.

### 2.1 Constraint-Compliance Verifier (제약 무시 F1)

- **소스 오브 트루스:** `drafts/draft_plan.md`, `data/analysis_plan.md`, `CLAUDE.md`의 사용자 제약, 그리고 현재 세션에서 사용자가 명시한 지시.
- **임무:** 산출물이 각 제약을 하나씩 지켰는지 점검.
  - tone & voice (draft_plan §2)
  - terminology decisions·forbidden terms (draft_plan §2A, `Style/terminology.md`)
  - table/figure plan 준수 (draft_plan §6)
  - 포함/제외기준·endpoint (analysis_plan)
  - 섹션별 forbidden content (drafting_protocol guardrails)
- **FAIL 조건:** 제약 위반이 하나라도 발견되면 FAIL. 위반 항목·위치·필요 조치를 명시.

### 2.2 Citation-Grounding Verifier (인용 환각 F2)

- **소스 오브 트루스:** `knowledge/evidence.md` (+ 해당 시 `knowledge/summaries/`).
- **Deterministic helper:** `py scripts\check_citations.py drafts\03_introduction.md --evidence knowledge\evidence.md`
- **임무:** 인용한 각 문장의 주장이 인용된 evidence 엔트리로 지지되는지 판정.
- **판정 기준 (모두 일치해야 SUPPORTED):** direction(방향), population(대상), intervention(중재), comparator(비교군), outcome(결과), statistical certainty(통계적 확실성).
- **추가 FAIL 조건:**
  - 인용한 `[EVID:id]`가 evidence.md에 없음 → FAIL (존재하지 않는 인용)
  - 해당 엔트리의 **Source Status**가 `todo` → FAIL (미검증 문헌)
  - verdict가 `UNSUPPORTED` 또는 `NOT_ENOUGH_INFORMATION` → FAIL
  - verdict가 `PARTIALLY_SUPPORTED` → 주장 문구를 약화(weaken)하거나 인용 교체 후 통과
- **판정 verdict:** `SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | NOT_ENOUGH_INFORMATION`

### 2.3 Data-Grounding Verifier (수치 조작 F3)

- **소스 오브 트루스:** `results/*.csv` (수치의 **유일한** 출처). table과 충돌 시 CSV가 우선하고 table을 flag.
- **임무:** 원고의 모든 결과 수치(n, %, mean±SD, median/IQR, p-value, CI, OR/HR/RR, timepoint)가 results CSV 셀로 추적되는지 확인.
- **제외 대상:** reference 연도, section/table/figure 번호, 버전 날짜, 저널 volume/issue.
- **허용오차:**
  | 유형 | 허용 |
  |---|---|
  | 정수 카운트 | 정확 일치만 |
  | 비율(%) | 원고 표기 정밀도로 반올림 일치 |
  | 평균/SD | 반올림 일치 (`54.3`는 `54.32` 일치, `55.1` 불일치) |
  | p-value | 반올림 일치 (`0.0004` → `p<0.001` 허용) |
  | CI 경계 | 각 경계가 소스 반올림값과 일치 |
  | 효과크기(OR/HR/RR) | 표기 정밀도로 반올림 일치 |
  | timepoint | analysis_plan/result label과 정확 일치 |
- **FAIL 조건:** CSV로 추적 불가능하거나 허용오차를 벗어난 수치 발견 시.

**Deterministic helper:** run `py scripts\check_numbers.py drafts\05_results.md drafts\table_1.md --results results` before LLM review.

---

### 2.4 Logic/Redundancy Verifier (논리·중복)

- **소스 오브 트루스:** 산출 섹션 자신과 인접 섹션(예: Results ↔ Discussion), `CLAUDE.md`의 Redundancy Prevention 규칙.
- **임무:** 섹션 간 논리 흐름과 중복을 점검한다. Results 수치가 Discussion에 그대로 반복되거나, Introduction에 결과 해석이 섞이는 등 섹션 역할 위반을 잡는다.
- **FAIL 조건:** 동일 데이터의 삼중 중복, 섹션 역할 위반, 또는 논리적 비약이 발견되면 FAIL.
- **게이트 원장 check key:** `logic`.

---

### 2.5 Ghost-Revision Checker (Phase 8)

- **입력:** `drafts/revision/REV{N}/response_letter_REV{N}.md`의 `[CHANGE]` blocks, original section files, revised section files.
- **명령:** `py scripts\check_revision_claims.py drafts\revision\REV1\response_letter_REV1.md --strict`
- **임무:** 응답서가 주장한 manuscript change가 실제 revised manuscript에 반영되었는지 확인한다.
- **확인 기준:**
  - `[CHANGE]` block에 `comment_id`, `section`, `expected_terms`가 있어야 한다.
  - revised section file이 존재해야 한다.
  - `expected_terms`가 revised section에 포함되어야 한다.
  - 응답서의 `Revised text:` 문구가 revised section에 실제로 있어야 한다.
  - original section file이 있으면 revised section이 original과 동일하지 않아야 한다.
- **FAIL 조건:** 위 조건 중 하나라도 불일치하면 `GATE FAIL`을 출력하고 Phase 8 gate를 통과시키지 않는다.

---

### 2.6 Style-Conformance Verifier (Phase 5 style-pass)

- **소스 오브 트루스:** `drafts/style_spec.md`(bound Style Spec), 지정 exemplar 앵커(`Style/own/` 또는 `Style/target_journal/`), `docs/writing_guide.md` 해당 섹션 규칙, `Style/terminology.md`. 외부 스타일 취향 금지.
- **임무:** `/style-pass` 변환(또는 revision 재작성) 후 각 섹션이 bound 스타일과 맞는지 점검한다 — 구조·흐름, 평균 문장 길이, hedging·claim 강도, 레퍼런스 형식, 용어, 섹션별 voice/tense. lint(기계)가 못 잡는 *전체 스타일* 레이어.
- **실행 시점:** deterministic lint(`lint_on_edit.py`/`lint_manuscript.py`) 다음. 프롬프트·출력 스키마는 `docs/verifier_prompt_templates.md`의 Style-Conformance Verifier.
- **FAIL 조건:** Style Spec 부재, 또는 구조·문장 길이·hedging·레퍼런스 형식·용어가 Spec과 어긋나거나 exemplar의 `Do Not Imitate` 항목을 모방하면 FAIL.
- **게이트 원장 check key:** `style`. 자율 루프(최대 2회)는 §3과 동일.

---

## 3. 자율 루프 규칙

### 3.1 루프 절차

1. **Produce** — 섹션(또는 claim 매핑, revision 응답)을 작성한다.
2. **Freeze & Verify** — 산출물을 고정(스냅샷)한 뒤 Verifier를 투입한다. 순서:
   - **(a) Deterministic helpers 먼저** — `check_citations.py`, `check_numbers.py`(해당 시 `check_revision_claims.py`)를 실행한다.
   - **(b) LLM Verifier 병렬** — Constraint / Citation / Data / Logic 네 Verifier는 서로 의존이 없으므로 **하나의 메시지에서 병렬 서브에이전트로 동시에** 투입한다. 각 Verifier에 **동일하게 고정된** 산출물 + 소스 오브 트루스를 전달한다. **검증이 끝날 때까지 산출물을 수정하지 않는다** — 수정은 모든 판정을 모은 뒤 한 번에 한다(병렬 검증 중 수정하면 일부 PASS가 낡은 상태 기준이 되어 무효해진다).
3. **판정 & 기록** — 모든 Verifier가 PASS면 게이트 원장에 `status: PASS`와 함께 **검증 시점 sha256를 `provenance:`에 기록**한다(§6 freshness). `artifact`는 필수; 인용 게이트는 `evidence`(`knowledge/evidence.md`), 수치 게이트는 `results`(해당 CSV)도 기록한다(revision 게이트는 evidence/results 필수). 이후 그 파일이 바뀌면 PASS는 stale(무효)이며 다음 `check_gate.py --verify-hash`에서 FAIL로 잡힌다.
4. **Fix loop** — 하나라도 FAIL이면 산출물을 수정하고 2단계로 돌아간다.
   - **수정 우선순위: Constraint(명세) 위반 먼저.** 명세 위반을 고치면 섹션이 재작성되어 다른 지적이 무의미해질 수 있으므로, 품질·문체 손질보다 명세 적합을 먼저 맞춘다.
   - 산출물이 바뀌었으므로 **이전 PASS를 모두 폐기하고 필요한 Verifier 전체를 재실행**한다(부분 재검증 금지). `provenance` 해시도 새로 기록한다.
5. **상한** — Fix→re-verify는 **최대 2회(N=2)**. 2회 후에도 FAIL이면 멈추고 게이트 원장에 `status: FAIL`을 기록한 뒤 사용자에게 미해결 지적사항만 보고한다(에스컬레이션).

### 3.2 Verifier 판정 출력 형식

PASS:
```
GATE PASS
verifier: Citation-Grounding
artifact: drafts/03_introduction.md
checked: 6 citations, 0 issues
```

FAIL (예시 — citation):
```
GATE FAIL
verifier: Citation-Grounding
artifact: drafts/06_discussion.md
sentence: "Prior studies demonstrated superior fusion rates [EVID:lee_2019]."
citation: EVID:lee_2019
verdict: UNSUPPORTED
reason: direction mismatch — Lee 2019 reports no significant difference in fusion rate
required_action: weaken claim or replace citation
```

FAIL (예시 — number):
```
GATE FAIL
verifier: Data-Grounding
artifact: drafts/05_results.md
sentence: "The treatment group improved by 55.1 points at 12 months."
number: 55.1 (mean)
closest_ground_truth: 54.32  (results/table2_outcomes.csv, row primary_outcome, col treatment_mean)
reason: no rounded match
required_action: replace with 54.3 or remove
```

---

## 4. Verifier 모델 정책

- **기본:** Opus.
- **예외:** Opus 사용 불가 시, 또는 사용자가 명시적으로 요청할 때 다른 모델(예: GPT-5.5) 사용 가능.
- 서브에이전트 dispatch 시 모델을 명시한다 (`model: opus` 기본).

---

## 5. Grounding 메커니즘

### 5.1 EVID 인용 태그

- 초안(Phase 3–6) 동안 모든 인용은 `[EVID:author_year]` 형식으로 표기한다.
  - 예: `[EVID:lee_2019]`, `[EVID:kim_2020]`
- 이 id는 `knowledge/evidence.md` 엔트리와 1:1로 묶인다 → 존재하지 않는 문헌 인용은 즉시 드러난다.
- Phase 7(Finalize)에서 목표 저널 형식(번호 또는 저자-연도)으로 변환한다.

### 5.2 results = 단일 진실

- 원고의 결과 수치는 `results/*.csv`에 존재하는 값만 허용한다.
- CSV에 없는 결과 수치를 prose에 새로 만들어 쓰지 않는다.

---

## 6. 게이트 원장 (Fail-Loudly)

- **위치:** `review/gates/phase_NN_<name>.GATE.md`
- **기록 주체:** Verifier 판정 후 메인 에이전트가 기록 (Verifier 출력을 옮김).
- **형식:** `review/gates/_TEMPLATE.GATE.md` 참조.
- **규칙:** 어떤 섹션/단계도 게이트 원장에 해당 산출물의 `status: PASS`가 없으면 다음으로 진행 금지.
- **Freshness (stale-gate guard):** PASS 기록 시 검증 대상 파일의 sha256를 `provenance:` 블록에 적고, 게이트 확인 시 `--verify-hash`로 재대조한다. 파일이 바뀌었으면 stale로 FAIL — **병렬 검증·revision 라운드에서 낡은 PASS가 살아남는 것을 막는다.** 해시 계산: `py scripts\check_gate.py --compute-hash drafts\05_results.md`.
- **Cross-check (ledger ↔ live):** `--require-check`는 원장이 `PASS`라고 *적혀 있는지*만 본다. 결정적 차원(`citation`/`numbers`/`revision_claims`)은 `--cross-check LABEL=PATH`로 **정본 checker를 즉석 재실행**해 원장 기록이 실제와 일치하는지 검증한다. checker를 돌리지 않고 적은 가짜 `PASS`, 또는 산출물이 바뀐 뒤 남은 stale `PASS`를 모순(contradiction)으로 잡는다. **live 체크가 FAIL이면 원장 내용과 무관하게 게이트 FAIL** — 깨진 산출물은 원장이 정직하게 FAIL을 적었더라도 통과할 수 없다(그 차원을 `--require-check`로 걸지 않았어도). 소스 미도달 시 조용히 통과하지 않고 **loud FAIL**. 이는 STOP Signals의 "PASS 받았으니 안전" 자기기만을 결정적으로 차단한다.
- **Deterministic ledger check:** `py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md --cross-check citation=drafts\05_results.md --cross-check numbers=drafts\05_results.md --results results`
- **Required order:** deterministic helpers (`check_citations.py`, `check_numbers.py`, `check_revision_claims.py`) → LLM verifier schema (`docs/verifier_prompt_templates.md`) → gate ledger entry → `check_gate.py` (`--verify-hash` freshness + `--cross-check` ledger↔live 대조 포함).

---

## 7. 게이트 배치 요약

| Phase | 게이트 | Verifier | 루프 단위 |
|---|---|---|---|
| 3 Draft Plan | Claim→Citation 사전검증 | Citation | 매핑 전체 |
| 4 Draft | 섹션 게이트 | Constraint + Citation + Data + Logic | 섹션 단위 (자율) |
| 5 Style-pass | style 게이트 | Style-Conformance | 섹션 단위 (자율) |
| 6 QC | 최종 확인 (경량) | — (인라인 게이트가 이미 수행) | 원고 전체 |
| 8 Revision | 응답 게이트 | Constraint + Citation + Data + ghost-revision diff + Response alignment | 응답 단위 (자율) |
