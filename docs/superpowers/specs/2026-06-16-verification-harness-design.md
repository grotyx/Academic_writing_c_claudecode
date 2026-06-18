# Verification Harness Design (검증 하네스 설계)

**Date:** 2026-06-16
**Status:** Implemented — see docs/superpowers/plans/2026-06-16-verification-harness.md
**Topic:** Academic paper writing workflow에 harness-engineering식 write→verify→write→verify 자동 루프 도입

---

## 1. Problem Statement

현재 워크플로의 검증은 두 가지 구조적 결함을 가진다:

1. **검증이 끝에 몰려 있음** — 모든 검증이 Phase 6 (QC)에서 한꺼번에 일어난다. 오류가 여러 섹션에 누적된 뒤에야 발견된다.
2. **검증이 수동·체크리스트 기반** — 사람이 qc_guide.md 체크리스트를 따라가며 확인한다. 모델이 자율적으로 검증하지 않으며, 모델이 지시·제약을 건너뛰어도 이를 막는 장치가 없다.

이로 인해 사용자가 보고한 3대 실패가 발생한다:

- **F1 (제약 무시):** 사용자가 건 제약·지시를 지키지 않고 진행한다.
- **F2 (인용 환각):** reference가 실재하는지/주장을 지지하는지 확인하지 않고 인용한다.
- **F3 (수치 조작):** 데이터 분석 후 실제 results와 다른 숫자를 원고에 쓴다.

## 2. Goals / Non-Goals

**Goals**
- 검증을 각 산출 단계 안으로 끌어와 **인라인 게이트**로 만든다 (planning 단계부터).
- produce → verify → fix → re-verify 루프를 **자율적으로** 돌린다 (섹션 단위).
- F1/F2/F3를 구조적으로 잡아내는 **grounding** 메커니즘을 도입한다.
- 게이트 통과 전 진행을 **막는다** (fail-loudly).

**Non-Goals**
- ~~새 Python 검증 스크립트는 만들지 않는다. (사용자 결정: 에이전트 + 프로토콜로만 구현)~~ *(superseded — 아래 갱신 참조)*
- 기존 `scripts/lint_manuscript.py`는 유지하되, 이번 하네스의 차단 메커니즘으로 삼지 않는다.

> **[2026-06-18 갱신]** 초기 '스크립트 없음' 결정은 번복됨 — 결정론적 helper 스크립트 5종(`scripts/check_citations.py`, `check_gate.py`, `check_numbers.py`, `check_revision_claims.py`, `compile_response_docx.py`)과 `tests/` pytest 스위트를 하네스에 추가했다. Verifier 서브에이전트는 이 스크립트를 먼저 실행한 뒤 LLM 판정을 수행한다 (deterministic-first). 아래 §3 D1, §4의 "스크립트 없음" 서술은 이 갱신으로 대체된다.

## 3. Decisions (확정)

| # | 결정 | 값 |
|---|------|-----|
| D1 | 강제 메커니즘 | Verifier 서브에이전트 + 프로토콜 규칙 + 결정론적 helper 스크립트 5종 (deterministic-first; ~~스크립트 없음~~ 번복 — §2 갱신 참조) |
| D2 | 루프 세밀도 / 자율성 | 섹션 단위 + 자율 루프 |
| D3 | 인용 grounding | 초안 작성 시 `[EVID:author_year]` 태그 사용, 최종 단계에서 저널 형식으로 변환 |
| D4 | 자율 루프 최대 재시도 | N = 2 (FAIL→fix→re-verify 2회까지, 이후 사용자 에스컬레이션) |
| D5 | Verifier 모델 | Opus 기본. Opus 불가 시 또는 사용자 요청 시 다른 모델(예: GPT-5.5) 허용 |

## 4. Core Concept — "Produce → Verify-Gate → Loop"

모든 산출 단계 뒤에 **검증 게이트**를 둔다.

```
[Produce artifact]
      │
      ▼
[Verifier subagent] ── 소스 오브 트루스와 적대적 대조
      │
   ┌──┴── FAIL ──► [Fix] ──► (re-verify, 최대 N=2회) ──► 에스컬레이션
   │
  PASS
   │
   ▼
[게이트 원장에 PASS 기록] ──► 다음 섹션/단계 진행 허용
```

- "차단"은 **게이트 원장(`review/gates/`) + 프로토콜 규칙**이 수행한다 (결정론적 helper 스크립트는 게이트 입력 신호를 만들고, 최종 차단은 원장의 `status: PASS` 유무로 강제).
- 원장에 해당 산출물의 `status: PASS`가 없으면 다음 단계 진행 금지.

## 5. The Three Verifiers (3대 실패에 매핑)

각 Verifier는 **헌장(charter)** 으로 정의되며, 외부지식 사용을 금지하고 주어진 소스만으로 판정한다.

### 5.1 Constraint-Compliance Verifier (→ F1)
- **소스 오브 트루스:** `drafts/draft_plan.md`, `data/analysis_plan.md`, `CLAUDE.md`에 명시된 사용자 제약
- **임무:** 산출물이 각 제약을 하나씩 지켰는지 확인. tone/voice, 금지 용어, table/figure 계획, 제외기준 등.
- **FAIL 조건:** 제약 위반 발견 시.

### 5.2 Citation-Grounding Verifier (→ F2)
- **소스 오브 트루스:** `knowledge/evidence.md` (+ `knowledge/summaries/`)
- **임무:** 인용된 각 문장의 주장이 해당 evidence 엔트리로 지지되는지 판정.
- **판정 기준:** 방향(direction), 대상(population), 중재(intervention), 비교군(comparator), 결과(outcome), 통계적 확실성이 모두 일치해야 SUPPORTED.
- **판정 출력:** `SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | NOT_ENOUGH_INFORMATION` + 근거 + 필요 조치(remove citation / weaken claim / replace citation / verify full text).
- **FAIL 조건:** 존재하지 않는 인용, 또는 UNSUPPORTED, 또는 evidence 엔트리 status가 `todo`.

### 5.3 Data-Grounding Verifier (→ F3)
- **소스 오브 트루스:** `results/*.csv` (숫자의 유일한 출처). 충돌 시 CSV가 table보다 우선.
- **임무:** 원고의 모든 결과 수치(n, %, mean±SD, median/IQR, p, CI, OR/HR/RR 등)가 results CSV 셀로 추적되는지 확인. reference 연도·section 번호·table 번호·버전 날짜는 제외.
- **허용오차:** 정수 카운트는 정확 일치; 평균/SD/비율/효과크기는 원고 표기 정밀도로 반올림 일치; p값은 반올림 일치(`0.0004` → `p<0.001` 허용).
- **FAIL 조건:** CSV/table로 추적 불가능한 수치 발견 시.

## 6. Grounding Mechanisms (조작을 구조적으로 어렵게)

- **EVID 인용 태그 (D3):** 초안에서 모든 인용은 `[EVID:author_year]` 형식. evidence.md 엔트리에 강제로 묶이므로, 존재하지 않는 문헌 인용은 즉시 드러난다. Phase 7에서 저널 형식(번호/저자-연도)으로 변환.
- **results = 단일 진실:** 원고 수치는 results CSV에 존재하는 값만 허용. 프로토콜이 "CSV에 없는 결과 수치를 prose에 쓰지 말 것"을 규정.

## 7. Gate Placement (검증을 앞으로 당김)

| Phase | 게이트 | 검증 내용 | 루프 단위 |
|-------|--------|-----------|-----------|
| 3 (Draft Plan) | Claim→Citation 사전검증 | ~20개 주장 각각을 Citation Verifier가 글쓰기 **전에** 검증 | 매핑 전체 |
| 4 (Draft) | 섹션 게이트 | 각 섹션 작성 직후 3 Verifier 동시 투입 → 자율 수정·재검증 | **섹션 단위 (자율)** |
| 6 (QC) | 최종 확인 | 인라인 검증 완료를 전제로 경량화된 최종 라운드 | 원고 전체 |
| 8 (Revision) | 응답 게이트 | 각 응답 작성 후 원고가 실제로 바뀌었는지 diff 대조 (ghost-revision 차단) | **응답 단위 (자율)** |

가장 강력한 anti-hallucination 지점은 **Phase 3** — 글을 쓰기 전에 근거 없는 주장을 거른다.

## 8. Revision Loop (Phase 8)

- **구조화된 변경 마커:** response letter의 각 변경 주장에 머신리더블 마커를 단다:
  ```
  [CHANGE]
  comment_id: R1-C3
  claim: eligibility criteria를 명확히 하는 문장 추가
  section: 04_methods
  expected_terms: eligibility criteria; excluded; prior surgery
  [/CHANGE]
  ```
- **Ghost-revision 검증:** Verifier가 (a) 해당 revised 섹션 파일이 존재하는지, (b) diff에 주장한 개념이 실제로 들어갔는지 대조. 응답은 "고쳤다"는데 원고가 안 바뀌었으면 FAIL.
- **자율 루프:** FAIL → 원고 수정 또는 응답 문구 수정 → 재검증 (N=2).

## 9. Fail-Loudly Enforcement — Gate Ledger

차단을 구현하는 핵심 장치. (원장 자체는 `status: PASS` 규칙으로 진행을 막고, `scripts/check_gate.py`가 원장 항목을 결정론적으로 검증한다 — §2 갱신 참조.)

- **위치:** `review/gates/phase_NN_*.GATE.md` (단계별 원장)
- **기록 주체:** Verifier 서브에이전트가 판정을 기록.
- **형식:**
  ```
  phase: Phase 4 — Draft Sections
  artifact: drafts/05_results.md
  status: PASS            # PASS | FAIL
  checks:
    citation: PASS
    numbers: PASS
    constraint: PASS
  round: 2                # 1차 FAIL → 수정 → 2차 PASS
  blocking_failures: none
  timestamp: 2026-06-16T14:30:00+09:00
  ```
- **프로토콜 규칙 (CLAUDE.md Critical Rule 신규):**
  > 어떤 섹션/단계도 `review/gates/`에 해당 산출물의 `status: PASS` 줄이 없으면 다음으로 진행 금지. 게이트 FAIL 시 작업을 멈추고 지적사항만 보고·수정한다. 재시도는 최대 2회, 이후 사용자에게 에스컬레이션.

## 10. Files to Create / Modify

**신규**
- `docs/verification_protocol.md` — 게이트 정의, Verifier 헌장(3종), 판정 출력 형식, 자율 루프 규칙(N=2), Verifier 모델 정책(Opus 기본/대체 허용), gate ledger 형식
- `review/gates/` 디렉터리 + 게이트 파일 템플릿 (+ `.gitkeep`)
- 결정론적 helper 스크립트 5종 — `scripts/check_citations.py`, `scripts/check_gate.py`, `scripts/check_numbers.py`, `scripts/check_revision_claims.py`, `scripts/compile_response_docx.py` (§2 갱신으로 추가; deterministic-first)
- `tests/` pytest 스위트 — helper 스크립트 회귀 테스트

**수정**
- `CLAUDE.md` — Critical Rules에 "게이트 통과 전 진행 금지" 추가; Recommended Workflow의 Phase 3/4/6/8에 게이트 명시; 모델 선택 표에 Verifier 모델 정책 추가; EVID 태그 규칙 추가
- `docs/drafting_protocol.md` — 섹션 단위 produce→verify→fix 루프 삽입
- `docs/qc_guide.md` — Phase 6를 인라인 검증과 중복 제거해 최종 확인용으로 경량화
- `docs/revision_guide.md` — `[CHANGE]` 마커 + revision 검증 루프 추가
- `docs/evidence_guide.md` — evidence.md 엔트리에 `source status`(verified/abstract-only/full-text-reviewed/todo) 필드 도입 (Citation Verifier가 참조)
- `docs/draft_plan_template.md` / `docs/writing_guide.md` — EVID 인용 태그 작성 규칙 반영
- README (en/ko/ja/zh) + 버전업

## 11. Verifier Model Policy (D5)

- 기본: **Opus**.
- 예외: Opus 사용 불가 시, 또는 사용자가 명시적으로 원할 때 다른 모델(예: GPT-5.5) 사용 가능.
- `docs/verification_protocol.md`에 정책으로 명문화.

## 12. Open Risks

- EVID 태그 도입은 작성 방식과 여러 문서(writing_guide, qc Round 2, 최종 변환)를 건드린다 → 일관성 유지 필요.
- 섹션 단위 자율 루프는 서브에이전트 호출이 많아 토큰 비용 증가 → N=2 상한으로 완화.
- Verifier가 LLM 판정이므로 100% 결정론적이지 않음 → 헌장에서 "외부지식 금지, 소스만 사용, 불확실 시 FAIL 기본값"으로 보수적 판정 유도.
