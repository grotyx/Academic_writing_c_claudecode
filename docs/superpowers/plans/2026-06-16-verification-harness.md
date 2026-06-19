# Verification Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** academic paper writing 워크플로에 harness-engineering식 produce→verify→fix→re-verify 자동 루프(검증 게이트)를 도입하여, 제약 무시(F1)·인용 환각(F2)·수치 조작(F3)을 각 단계에서 구조적으로 차단한다.

**Architecture:** **Verifier 서브에이전트 + 프로토콜 규칙 + 결정론적 helper 스크립트**로 구현. 신규 키스톤 문서 `docs/verification_protocol.md`가 Verifier 헌장·게이트 정의·자율 루프(N=2)·게이트 원장 형식을 정의하고, 기존 문서들(CLAUDE.md, drafting_protocol, evidence_guide, draft_plan_template, writing_guide, qc_guide, revision_guide)이 이를 참조하도록 수정. 차단은 `review/gates/` 원장에 `status: PASS`가 없으면 진행 금지하는 규칙으로 강제.

> **[2026-06-18 갱신]** 초기 '새 스크립트 없음 / 코드·테스트 없음' 결정은 번복됨 — 결정론적 helper 스크립트 5종(`scripts/check_citations.py`, `check_gate.py`, `check_numbers.py`, `check_revision_claims.py`, `compile_response_docx.py`)과 `tests/` pytest 스위트를 하네스에 추가했다 (deterministic-first: 스크립트가 먼저 돌고 그 뒤 LLM 판정). 아래 Architecture·Tech Stack의 "스크립트 없음 / 코드·테스트 없음" 서술은 이 갱신으로 대체된다.

> **[2026-06-19 갱신]** 본 문서의 'Verifier 3종 / 3 Verifier 헌장'은 초기 설계 기준이다. 구현에서 Logic이 추가되어 draft gate는 4종(Constraint·Citation·Data·Logic), Revision gate는 Revision-claims·Response-alignment를 더한다. 최신 verifier 세트 정의는 `docs/verification_protocol.md`·`CLAUDE.md` Rule 10을 따른다.

**Tech Stack:** Markdown 문서, Claude Code 서브에이전트(Agent tool), Python 결정론적 helper 스크립트 + `tests/` pytest 스위트, git. (~~코드/테스트 없음~~ 번복 — 위 갱신 참조; pytest와 더불어 일관성 grep·lint 실행·교차 확인을 병행한다.)

**Source spec:** `docs/superpowers/specs/2026-06-16-verification-harness-design.md`

---

## File Structure

| File | 역할 | Task |
|---|---|---|
| `docs/verification_protocol.md` (신규) | 키스톤. 게이트·3 Verifier 헌장·루프·원장·EVID 태그 정의 | 1 |
| `review/gates/.gitkeep` + `review/gates/_TEMPLATE.GATE.md` (신규) | 게이트 원장 디렉터리·템플릿 | 2 |
| `CLAUDE.md` (수정) | Critical Rule 10 추가, Phase 게이트 명시, 모델표, 버전 v0.9.0 | 3 |
| `docs/drafting_protocol.md` (수정) | 섹션 단위 verify→fix 루프 삽입 | 4 |
| `docs/evidence_guide.md` (수정) | entry에 `Source Status` 필드 추가 | 5 |
| `docs/draft_plan_template.md` + `docs/writing_guide.md` (수정) | EVID 인용 태그 규칙 | 6 |
| `docs/qc_guide.md` (수정) | Phase 6를 인라인 게이트와 중복 제거해 최종 확인용으로 경량화 | 7 |
| `docs/revision_guide.md` (수정) | `[CHANGE]` 마커 + revision 검증 게이트 | 8 |
| `README*.md` (수정) | 버전·changelog | 9 |

각 task는 독립적으로 의미 있는 커밋을 만든다. Task 1이 키스톤이므로 먼저 수행한다.

---

## Task 1: 키스톤 문서 `docs/verification_protocol.md` 생성

**Files:**
- Create: `docs/verification_protocol.md`

- [ ] **Step 1: 파일을 아래 내용 그대로 생성**

````markdown
# Verification Protocol (검증 하네스) (v0.1.0)

> harness-engineering식 produce→verify→fix→re-verify 자동 루프 정의.
> 각 산출 단계 뒤에 검증 게이트를 두어 제약 무시·인용 환각·수치 조작을 차단한다.
> 검증은 **Verifier 서브에이전트 + 프로토콜 규칙**으로만 수행한다 (검증 전용 스크립트 없음).

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

## 2. 세 개의 Verifier (헌장)

모든 Verifier는 공통 규칙을 따른다:
- **외부지식 사용 금지.** 주어진 소스(소스 오브 트루스)와 산출물만으로 판정한다.
- **불확실하면 FAIL 기본값.** 지지 여부가 모호하면 PASS로 넘기지 않는다.
- **판정 결과를 구조화 출력**한다 (3.2 형식).

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

---

## 3. 자율 루프 규칙

### 3.1 루프 절차

1. **Produce** — 섹션(또는 claim 매핑, revision 응답)을 작성한다.
2. **Verify** — 해당 게이트의 Verifier(들)를 서브에이전트로 투입한다. 각 Verifier에 산출물 + 소스 오브 트루스를 전달한다.
3. **판정** — 모든 Verifier가 PASS면 게이트 원장에 `status: PASS` 기록 후 다음 단계.
4. **Fix loop** — 하나라도 FAIL이면 지적사항을 수정하고 2단계로 돌아간다.
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

---

## 7. 게이트 배치 요약

| Phase | 게이트 | Verifier | 루프 단위 |
|---|---|---|---|
| 3 Draft Plan | Claim→Citation 사전검증 | Citation | 매핑 전체 |
| 4 Draft | 섹션 게이트 | Constraint + Citation + Data | 섹션 단위 (자율) |
| 6 QC | 최종 확인 (경량) | — (인라인 게이트가 이미 수행) | 원고 전체 |
| 8 Revision | 응답 게이트 | Constraint + Citation + Data + ghost-revision diff | 응답 단위 (자율) |
````

- [ ] **Step 2: 일관성 검증**

Run: `py scripts/lint_manuscript.py docs/verification_protocol.md --quiet` (Windows)
Expected: 치명적 오류 없음 (스타일 경고는 무시 가능). 스크립트가 단일 파일을 받지 않으면 `py scripts/lint_manuscript.py docs --quiet`로 대체 실행.

Grep로 핵심 앵커가 존재하는지 확인 — Verifier 3종, N=2, 게이트 원장이 모두 들어갔는지:
Run: `grep -E "Constraint-Compliance|Citation-Grounding|Data-Grounding|최대 2회|review/gates" docs/verification_protocol.md`
Expected: 각 패턴이 1회 이상 매칭.

- [ ] **Step 3: Commit**

```bash
git add docs/verification_protocol.md
git commit -m "docs: add verification protocol (3 verifiers, gate loop)"
```

---

## Task 2: 게이트 원장 디렉터리·템플릿 생성

**Files:**
- Create: `review/gates/.gitkeep`
- Create: `review/gates/_TEMPLATE.GATE.md`

- [ ] **Step 1: `.gitkeep` 생성 (빈 파일)**

빈 파일로 생성하여 빈 디렉터리를 git에 보존한다.

- [ ] **Step 2: `review/gates/_TEMPLATE.GATE.md`를 아래 내용으로 생성**

```markdown
# Gate Ledger Template

> 각 게이트 통과/실패를 기록한다. Phase별로 복사하여 사용:
> `review/gates/phase_04_draft.GATE.md` 등.
> 규칙: 어떤 섹션/단계도 여기에 status: PASS 줄이 없으면 다음으로 진행 금지.

## Entry 형식

```
phase: Phase 4 — Draft Sections
artifact: drafts/05_results.md
status: PASS              # PASS | FAIL
checks:
  constraint: PASS
  citation: PASS
  numbers: PASS
round: 2                  # 1차 FAIL → 수정 → 2차 PASS (최대 2회)
blocking_failures: none   # FAIL 시 미해결 지적사항 요약
verifier_model: opus
timestamp: 2026-06-16T14:30:00+09:00
```

## 예시 (FAIL 후 에스컬레이션)

```
phase: Phase 4 — Draft Sections
artifact: drafts/06_discussion.md
status: FAIL
checks:
  constraint: PASS
  citation: FAIL
  numbers: PASS
round: 2
blocking_failures: EVID:lee_2019 direction mismatch (UNSUPPORTED) — 사용자 확인 필요
verifier_model: opus
timestamp: 2026-06-16T15:10:00+09:00
```
```

- [ ] **Step 3: 검증**

Run: `git status --porcelain review/gates/`
Expected: `review/gates/.gitkeep`와 `review/gates/_TEMPLATE.GATE.md` 두 파일이 추가됨(`??` 또는 `A`).

- [ ] **Step 4: Commit**

```bash
git add review/gates/.gitkeep review/gates/_TEMPLATE.GATE.md
git commit -m "docs: add gate ledger directory and template"
```

---

## Task 3: `CLAUDE.md` — Critical Rule 10 + Phase 게이트 + 모델표 + 버전업

**Files:**
- Modify: `CLAUDE.md` (헤더 버전, Critical Rules, Recommended Workflow, Model Selection 표)

- [ ] **Step 1: 헤더 버전 업데이트**

찾기: `# Academic Paper Writing Project (v0.8.1)`
바꾸기: `# Academic Paper Writing Project (v0.9.0)`

- [ ] **Step 2: Critical Rules에 Rule 10 추가**

`### 9. Model Selection by Phase` 섹션 **앞**(즉 Rule 8과 9 사이가 아니라, Rule 9 직전이 자연스러우면 Rule 9 앞, 아니면 Rule 9 뒤)에 아래를 삽입. 권장: 기존 Rule 9 블록 바로 앞에 삽입하고 번호 충돌이 없도록 신규 번호 **10**으로 명명하되 위치는 Rule 8 다음.

실제 삽입 위치: `### 8. Draft Plan Mandatory` 블록이 끝나고 `### 9. Model Selection by Phase`가 시작되기 직전. 아래 블록을 그 사이에 넣는다.

```markdown
### 10. Verification Gates Mandatory (검증 게이트 필수)

> **각 산출 단계 뒤에 검증 게이트를 통과해야 다음으로 진행할 수 있다.**
> 상세: `docs/verification_protocol.md`

**규칙:**

- **NEVER proceed past a gate without a recorded PASS.** `review/gates/`의 해당 산출물 항목에 `status: PASS`가 없으면 다음 섹션/단계 진행을 거부한다.
- 검증은 **Verifier 서브에이전트**로 수행한다 (Constraint / Citation / Data 3종). 외부지식 금지, 소스 오브 트루스(draft_plan·analysis_plan·evidence.md·results CSV)와만 대조.
- FAIL 시 **자율 수정 루프**: 지적사항을 고쳐 재검증. 최대 **2회(N=2)**, 이후 사용자에게 에스컬레이션.
- **Verifier 모델:** Opus 기본. Opus 불가 시 또는 사용자 요청 시 다른 모델(예: GPT-5.5) 허용.
- **인용 grounding:** 초안에서 모든 인용은 `[EVID:author_year]` 태그로 표기 (Phase 7에서 저널 형식 변환).
- **수치 grounding:** 원고 결과 수치는 `results/*.csv`에 존재하는 값만 사용.

**게이트 배치:**

| Phase | 게이트 | Verifier |
|-------|--------|----------|
| 3 (Draft Plan) | Claim→Citation 사전검증 | Citation |
| 4 (Draft) | 섹션 단위 (자율 루프) | Constraint + Citation + Data |
| 6 (QC) | 최종 확인 (경량) | 인라인 게이트가 이미 수행 |
| 8 (Revision) | 응답 단위 (자율 루프) | Constraint + Citation + Data + ghost-revision |
```

- [ ] **Step 3: Model Selection 표에 Verifier 행 추가**

`### 9. Model Selection by Phase` 표(`| Phase | 권장 모델 | 대안 모델 | 이유 |`)의 마지막 데이터 행(`Phase 8: Revision`) 다음에 추가:

```markdown
| **Verifier (모든 Phase)** | **Opus (기본)**     | GPT-5.5 등 (Opus 불가/요청 시) | 검증 품질이 하네스 신뢰성을 좌우          |
```

- [ ] **Step 4: Recommended Workflow에 게이트 명시**

`Phase 3: Draft Plan` 블록의 `├── 사용자 확인 후 Phase 4 진행` 줄 **앞**에 추가:
```
├── 🔒 GATE: Claim→Citation 사전검증 (Citation Verifier) — 근거 없는 claim은 글쓰기 전 차단
```

`Phase 4: Draft` 블록의 `├── 02_abstract.md     → summary (write LAST)` 줄 **앞**(섹션 나열 직후, 즉 title 다음)에 추가:
```
├── 🔒 GATE (각 섹션마다): Constraint + Citation + Data Verifier 자율 루프 (최대 2회) → review/gates/ 기록
```
(실제로는 Phase 4 블록 마지막 줄 다음, Phase 5 시작 전에 위 GATE 줄을 넣어도 무방하다. 핵심은 Phase 4 안에 섹션 게이트가 명시되는 것.)

`Phase 8: Revision` 블록의 `├── QC re-run (최소 Round 1-2 재수행)` 줄 **앞**에 추가:
```
├── 🔒 GATE (각 응답마다): ghost-revision 검증 (응답 주장 ↔ 원고 diff 대조) 자율 루프
```

- [ ] **Step 5: File Roles 표에 신규 문서 등록**

`| File/Folder | Purpose | When to Use |` 표에서 `docs/revision_guide.md` 행 다음에 추가:
```markdown
| `docs/verification_protocol.md` | 검증 게이트·3 Verifier 헌장·자율 루프·게이트 원장 정의 | Phase 3·4·6·8 (게이트 수행 시 **반드시** 참조) |
```

- [ ] **Step 6: 검증**

Run: `grep -n "v0.9.0\|Verification Gates Mandatory\|verification_protocol.md\|review/gates" CLAUDE.md`
Expected: 버전 v0.9.0, Rule 10 제목, 신규 문서 참조, 게이트 원장 참조가 모두 매칭.

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add verification gate critical rule and phase gates (v0.9.0)"
```

---

## Task 4: `docs/drafting_protocol.md` — 섹션 단위 verify→fix 루프 삽입

**Files:**
- Modify: `docs/drafting_protocol.md` (Step 6 다음에 Step 7 추가, Completion Checklist 갱신)

- [ ] **Step 1: Step 7 (Verification Gate) 추가**

`### Step 6. Lint and QC Pass` 블록(끝: "Address high-priority findings before considering the section complete.")과 그 다음 `---` 사이에, 아래를 삽입:

```markdown
### Step 7. Verification Gate (자율 루프)

섹션 작성이 끝나면 다음 단계로 넘어가기 전에 검증 게이트를 통과해야 한다.
상세: `docs/verification_protocol.md`.

1. 세 Verifier 서브에이전트를 투입한다 (모델: Opus 기본):
   - **Constraint** — draft_plan·analysis_plan·사용자 제약 준수
   - **Citation** — `[EVID:id]` 인용이 evidence.md로 지지되는지 (방향·대상·비교군·결과 일치)
   - **Data** — 모든 결과 수치가 `results/*.csv`로 추적되는지
2. 모두 PASS → `review/gates/phase_04_draft.GATE.md`에 `status: PASS` 기록 → 다음 섹션.
3. FAIL → 지적사항을 수정하고 재검증. 최대 2회(N=2), 이후 사용자에게 에스컬레이션.

게이트 PASS가 원장에 기록되기 전에는 다음 섹션을 시작하지 않는다.
```

- [ ] **Step 2: Completion Checklist에 게이트 항목 추가**

`## Completion Checklist`의 마지막 항목(`- [ ] scripts/lint_manuscript.py was run and findings were addressed or documented.`) 다음에 추가:

```markdown
- [ ] Verification gate (Constraint/Citation/Data) passed and recorded in `review/gates/`.
```

- [ ] **Step 3: 검증**

Run: `grep -n "Verification Gate\|review/gates\|Constraint\|Citation\|Data" docs/drafting_protocol.md`
Expected: Step 7 제목과 3 Verifier, 게이트 원장 참조가 매칭.

- [ ] **Step 4: Commit**

```bash
git add docs/drafting_protocol.md
git commit -m "docs: insert section-level verification gate into drafting protocol"
```

---

## Task 5: `docs/evidence_guide.md` — entry에 `Source Status` 필드 추가

**Files:**
- Modify: `docs/evidence_guide.md` (entry 기본 형식, 헤더 버전, 체크리스트)

- [ ] **Step 1: 헤더 버전 업데이트**

찾기: `# Evidence 작성 가이드 (v0.2.2)`
바꾸기: `# Evidence 작성 가이드 (v0.3.0)`

- [ ] **Step 2: entry 기본 형식에 Source Status 필드 추가**

`### 기본 형식` 코드블록에서 아래 줄을 찾는다:
```
- **PDF:** knowledge/pdf/파일명.pdf (또는 "No PDF - abstract only")
```
그 **다음 줄**에 추가:
```
- **Source Status:** verified | abstract-only | full-text-reviewed | todo
```

- [ ] **Step 3: Source Status 설명 추가**

`### 작성 원칙` 섹션이 시작되기 직전(`### 기본 형식` 블록 종료 후)에 아래 소절을 삽입:

```markdown
### Source Status 필드 (검증 게이트 연동)

> Citation-Grounding Verifier가 이 필드를 확인한다. 상세: `docs/verification_protocol.md`.

| 값 | 의미 | 인용 가능 여부 |
|----|------|----------------|
| `verified` | 서지정보·핵심 주장 확인 완료 | 인용 가능 |
| `abstract-only` | 초록만 확인 (전문 미확인) | 초록이 지지하는 범위 내에서만 인용 |
| `full-text-reviewed` | 전문 정독 완료 | 인용 가능 (가장 신뢰) |
| `todo` | 미확인 (등록만 됨) | **인용 금지** — 게이트에서 FAIL |

`todo` 상태의 문헌을 인용하면 검증 게이트가 차단한다. 인용 전 반드시 `verified` 이상으로 올린다.
```

- [ ] **Step 4: 체크리스트에 항목 추가**

`## Checklist: 좋은 Evidence Entry`의 마지막 항목(`- [ ] PDF 파일명이 규칙에 맞게 저장되었는가?`) 다음에 추가:
```markdown
- [ ] Source Status가 기록되었는가? (인용하려면 `verified` 이상)
```

- [ ] **Step 5: 검증**

Run: `grep -n "Source Status\|todo\|v0.3.0" docs/evidence_guide.md`
Expected: 버전, Source Status 필드, 4개 상태값(verified/abstract-only/full-text-reviewed/todo)이 매칭.

- [ ] **Step 6: Commit**

```bash
git add docs/evidence_guide.md
git commit -m "docs: add Source Status field to evidence entries for citation gate"
```

---

## Task 6: EVID 인용 태그 규칙 — `draft_plan_template.md` + `writing_guide.md`

**Files:**
- Modify: `docs/draft_plan_template.md` (Claim→Citation 매핑에 EVID id 반영)
- Modify: `docs/writing_guide.md` (General Principles에 EVID 태그 규칙)

- [ ] **Step 1: draft_plan_template.md — Claim→Citation 매핑에 EVID 안내 추가**

`## 5. Claim → Citation Mapping` 블록의 인용 인용문(`> Style/own/에서 본인 논문 스타일 앵커도 확인.`) 다음 줄에 추가:
```markdown
> **인용 형식:** citation은 `[EVID:author_year]` 태그로 적는다 (evidence.md id와 일치). 존재하지 않는 id는 게이트에서 차단된다.
```

- [ ] **Step 2: draft_plan_template.md — 승인 체크리스트에 EVID 항목 추가**

`## 승인 체크리스트 (Phase 4 진행 전 확인)`의 `- [ ] 5. Claim→Citation mapping — ~20개 claim에 citation 모두 확보` 항목을 아래로 교체:
```markdown
- [ ] 5. Claim→Citation mapping — ~20개 claim에 citation 모두 확보 (`[EVID:id]` 형식, evidence.md 존재 확인)
```

- [ ] **Step 3: writing_guide.md — General Principles에 EVID 태그 규칙 추가**

먼저 삽입 위치를 확인한다:
Run: `grep -n "General Principles\|약어\|Abbreviation" docs/writing_guide.md`

`General Principles` 섹션 안, 약어 정의 규칙 근처(또는 General Principles의 마지막 규칙 다음)에 아래 항목을 추가한다. 정확한 줄은 grep 결과로 판단하되, General Principles 목록의 한 항목으로 넣는다:

```markdown
- **인용 태그(EVID):** 초안 단계에서 모든 인용은 `[EVID:author_year]` 형식으로 표기한다 (예: `[EVID:lee_2019]`). 이 id는 `knowledge/evidence.md` 엔트리와 일치해야 하며, Phase 7(Finalize)에서 목표 저널 형식(번호 또는 저자-연도)으로 변환한다. 상세: `docs/verification_protocol.md`.
```

- [ ] **Step 4: 검증**

Run: `grep -n "EVID:author_year\|EVID:lee_2019" docs/draft_plan_template.md docs/writing_guide.md`
Expected: 두 파일 모두에서 EVID 태그 규칙이 매칭.

- [ ] **Step 5: Commit**

```bash
git add docs/draft_plan_template.md docs/writing_guide.md
git commit -m "docs: add EVID citation tag convention to draft plan and writing guide"
```

---

## Task 7: `docs/qc_guide.md` — Phase 6 경량화 (인라인 게이트와 중복 제거)

**Files:**
- Modify: `docs/qc_guide.md` (헤더 버전, Overview에 인라인 게이트 연동 명시)

- [ ] **Step 1: 헤더 버전 업데이트**

찾기: `# Quality Control Guide (v0.4.0)`
바꾸기: `# Quality Control Guide (v0.5.0)`

- [ ] **Step 2: Overview에 인라인 게이트 연동 블록 추가**

`## Overview` 블록(끝: "모든 검증 결과는 `review/qc_log.md`에 기록합니다.") 다음에 아래를 삽입:

```markdown
> **인라인 게이트 연동 (v0.5.0):** Phase 4 드래프팅 중 섹션마다 Constraint/Citation/Data Verifier 게이트가 이미 수행된다 (`docs/verification_protocol.md`). 따라서 Phase 6 QC는 처음부터 다시 검사하는 단계가 아니라, **인라인 게이트 결과를 전제로 한 최종 확인**이다.
> - Round 1 (숫자) · Round 2 (인용)은 인라인 Data/Citation 게이트가 통과된 섹션에 대해 **교차·전체 일관성**만 확인한다 (게이트가 잡지 못한 섹션 간 불일치).
> - `review/gates/`에 PASS 기록이 없는 섹션이 있으면 QC를 진행하지 말고 해당 섹션의 게이트를 먼저 통과시킨다.
> - Round 3–6은 종전대로 수행한다.
```

- [ ] **Step 3: 검증**

Run: `grep -n "v0.5.0\|인라인 게이트\|review/gates\|verification_protocol" docs/qc_guide.md`
Expected: 버전, 인라인 게이트 연동 문구, 게이트 원장·프로토콜 참조가 매칭.

- [ ] **Step 4: Commit**

```bash
git add docs/qc_guide.md
git commit -m "docs: link Phase 6 QC to inline verification gates (lighten, v0.5.0)"
```

---

## Task 8: `docs/revision_guide.md` — `[CHANGE]` 마커 + revision 검증 게이트

**Files:**
- Modify: `docs/revision_guide.md` (헤더 버전, Response Letter 구조에 [CHANGE] 마커, QC Re-run에 ghost-revision 게이트)

- [ ] **Step 1: 헤더 버전 업데이트**

찾기: `# Revision & Reviewer Response Guide (v0.4.1)`
바꾸기: `# Revision & Reviewer Response Guide (v0.5.0)`

- [ ] **Step 2: [CHANGE] 마커 소절 추가**

`### 형식 규칙` 표가 끝나고 `### 본문 수정 원칙`이 시작되기 직전에 아래 소절을 삽입:

```markdown
### 변경 추적 마커 ([CHANGE]) — 검증 게이트용

> ghost-revision(응답서는 "고쳤다"는데 원고는 안 바뀐 경우)을 검증 게이트가 잡아내기 위한 머신리더블 마커.
> 응답서의 **최종본**에서는 이 마커를 제거하고, 작업·검증 중에만 유지한다 (또는 주석으로 보관).

응답에서 원고 변경을 주장할 때마다 아래 마커를 첨부한다:

```
[CHANGE]
comment_id: R1-C3
claim: eligibility criteria를 명확히 하는 문장 추가
section: 04_methods
expected_terms: eligibility criteria; excluded; prior surgery
[/CHANGE]
```

검증 게이트는 (a) 해당 revised 섹션 파일 존재, (b) diff에 `expected_terms`가 실제로 추가되었는지 대조한다. 불일치 시 FAIL → 원고를 고치거나 응답 문구를 수정한다 (최대 2회).
```

- [ ] **Step 3: QC Re-run에 ghost-revision 게이트 추가**

`## QC Re-run for Revision` 섹션의 `### Revision QC 실행 원칙` 번호 목록 마지막 항목(`4. **응답서 제출 전 최종 Round 1 검증** ...`) 다음에 추가:

```markdown
5. **Ghost-revision 게이트 (필수):** 각 응답의 `[CHANGE]` 마커마다 원고 diff를 대조하여 주장한 변경이 실제로 반영됐는지 확인한다. Constraint/Citation/Data Verifier도 변경된 섹션에 재투입한다. 결과를 `review/gates/phase_08_revision.GATE.md`에 기록한다. 상세: `docs/verification_protocol.md`.
```

- [ ] **Step 4: Revision 후 체크리스트에 항목 추가**

`### Revision 후 체크리스트 (제출 전)`의 마지막 항목(`- [ ] QC log 업데이트 ...`) 다음에 추가:
```markdown
- [ ] Ghost-revision 게이트 통과 — 모든 [CHANGE] 주장이 원고 diff로 확인됨 (`review/gates/phase_08_revision.GATE.md`)
```

- [ ] **Step 5: 검증**

Run: `grep -n "v0.5.0\|\[CHANGE\]\|ghost-revision\|Ghost-revision\|expected_terms" docs/revision_guide.md`
Expected: 버전, [CHANGE] 마커, ghost-revision 게이트, expected_terms가 매칭.

- [ ] **Step 6: Commit**

```bash
git add docs/revision_guide.md
git commit -m "docs: add [CHANGE] markers and ghost-revision gate to revision guide"
```

---

## Task 9: README 업데이트 + 버전 + 스펙 상태 갱신

**Files:**
- Modify: `README.md`, `README.ko.md` (버전 + changelog), `README.ja.md`, `README.zh.md` (버전만)
- Modify: `docs/superpowers/specs/2026-06-16-verification-harness-design.md` (Status)

- [ ] **Step 1: 각 README 버전 문자열 교체**

먼저 위치 확인:
Run: `grep -n "0.8.1\|v0.8.1" README.md README.ko.md README.ja.md README.zh.md`

각 파일에서 `0.8.1` → `0.9.0` (또는 `v0.8.1` → `v0.9.0`) 로 교체. grep 결과의 각 매칭을 정확히 교체한다.

- [ ] **Step 2: README.md changelog에 v0.9.0 항목 추가**

`README.md`의 changelog 섹션에서 가장 최근 버전 항목(v0.8.1) **앞**에 추가:

```markdown
### v0.9.0 — Verification Harness
- Inline verification gates after each produce step (Phase 3/4/8) — replaces end-loaded manual QC with a produce→verify→fix→re-verify loop
- Three Verifier subagents: Constraint (instruction compliance), Citation (citation grounding vs evidence.md), Data (numbers vs results CSV)
- Autonomous fix loop (max 2 retries) then user escalation
- `[EVID:author_year]` citation tags and results-CSV-as-single-source grounding
- Gate ledger (`review/gates/`) blocks progress until `status: PASS` is recorded
- New `docs/verification_protocol.md`; `evidence.md` gains a Source Status field
```

- [ ] **Step 3: README.ko.md changelog에 동일 항목(한국어) 추가**

`README.ko.md`의 changelog에서 v0.8.1 항목 앞에 추가:

```markdown
### v0.9.0 — 검증 하네스
- 각 산출 단계(Phase 3/4/8) 뒤 인라인 검증 게이트 — 끝에 몰린 수동 QC를 produce→verify→fix→re-verify 루프로 전환
- 3개 Verifier 서브에이전트: Constraint(지시 준수), Citation(evidence.md 대조 인용 검증), Data(results CSV 대조 수치 검증)
- 자율 수정 루프(최대 2회) 후 사용자 에스컬레이션
- `[EVID:author_year]` 인용 태그 + results CSV 단일 진실 grounding
- 게이트 원장(`review/gates/`)이 `status: PASS` 기록 전 진행을 차단
- 신규 `docs/verification_protocol.md`; `evidence.md`에 Source Status 필드 추가
```

- [ ] **Step 4: 스펙 Status 갱신**

`docs/superpowers/specs/2026-06-16-verification-harness-design.md`에서:
찾기: `**Status:** Approved (design) — pending implementation plan`
바꾸기: `**Status:** Implemented — see docs/superpowers/plans/2026-06-16-verification-harness.md`

- [ ] **Step 5: 검증**

Run: `grep -rn "0.9.0" README.md README.ko.md README.ja.md README.zh.md`
Expected: 4개 파일 모두에서 0.9.0이 매칭. README.md·README.ko.md에는 changelog 항목도 매칭.

Run: `py scripts/lint_manuscript.py docs --quiet` (있으면)
Expected: 치명적 오류 없음.

- [ ] **Step 6: Commit**

```bash
git add README.md README.ko.md README.ja.md README.zh.md docs/superpowers/specs/2026-06-16-verification-harness-design.md
git commit -m "docs: bump to v0.9.0 and document verification harness in READMEs"
```

- [ ] **Step 7: Push (전체 작업 완료 후)**

```bash
git push
```

---

## Self-Review Notes

- **Spec coverage:** spec §10의 모든 파일이 task로 매핑됨 — verification_protocol(T1), gates(T2), CLAUDE.md(T3), drafting_protocol(T4), evidence_guide(T5), draft_plan/writing_guide(T6), qc_guide(T7), revision_guide(T8), README+버전(T9). 3 Verifier(spec §5)는 T1, EVID/results grounding(spec §6)은 T1·T3·T5·T6, 게이트 배치(spec §7)는 T3·T4·T7·T8, revision 루프(spec §8)는 T8, 게이트 원장(spec §9)은 T1·T2, 모델 정책(spec §11)은 T1·T3에 반영됨.
- **용어 일관성:** 세 Verifier 명칭을 모든 문서에서 `Constraint`/`Citation`/`Data`로 통일. 게이트 원장 경로는 `review/gates/`로 통일. 재시도 상한은 `N=2`로 통일.
- **No placeholders:** 모든 수정 step에 실제 삽입 텍스트와 정확한 앵커(찾기/바꾸기 문자열, 인접 줄)를 제시함.
- **주의:** writing_guide.md(T6 Step 3)와 README changelog 위치(T9)는 파일이 커서 grep으로 정확한 앵커를 먼저 확인한 뒤 삽입한다. 줄 번호는 drift 가능하므로 헤딩·인접 텍스트 기준으로 위치를 잡는다.
