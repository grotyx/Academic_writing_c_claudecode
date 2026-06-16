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
