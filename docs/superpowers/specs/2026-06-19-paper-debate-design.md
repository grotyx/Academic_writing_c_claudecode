# Paper-Debate: Claude–Codex Co-Author Debate (설계)

**Date:** 2026-06-19
**Status:** Designed — pending implementation plan
**Topic:** 논문 작성의 사고 단계(planning·통계 계획·논문 계획·논리/문단 구조·revision 대응)에서 Claude와 Codex가 **co-author**로 협력 토론하여, 합의된 방향을 바탕으로 산출물을 작성한다.

---

## 1. Problem / Goal

AI 단독 작성은 한 모델의 blind spot에 갇힌다. 통계 방법 선택, 논문 framing, 논증 구조 같은 "방향 결정"은 서로 다른 관점의 검토에서 품질이 오른다. 이 워크플로에 두 모델(Claude + Codex)이 **co-author로서 작성 전에 방향을 토론·합의**하는 단계를 도입한다.

**Goal**
- 사고 단계(주로 계획·구조)에서 Claude와 Codex가 합의된 방향을 도출하고, 그 합의로 산출물(plan/draft/response)을 작성한다.
- 토론은 **작성 전**에 수행하여 재작업을 줄인다.
- 토론 과정과 합의를 추적 가능하게 기록한다.

**Non-Goals**
- 적대적 reviewer 시뮬레이션(완성본 공격)은 **별도 sub-project B** (§7).
- 실시간 양방향 스트리밍 대화 — Codex 호출은 forwarder 구조(요청→응답 사이클).
- 토론을 통과 필수 게이트로 만들지 않음 — **품질 보조**이며, 안 해도 워크플로는 정상 진행.

## 2. Decisions (확정)

| # | 결정 | 값 |
|---|------|-----|
| D1 | 협업 형태 | 토론형(Debate) — 입장→반박→수렴. 단 **co-author 협력 프레임**(대립 아님) |
| D2 | 발동 | 핵심 단계 **자동 제안** + **수동 명령** `/paper-debate` |
| D3 | 깊이 | 합의까지, **상한 3라운드**. 미합의 시 차이점 + Claude 추천 → 사용자 결정 |
| D4 | 시점 | **작성 전** 토론 → 합의 → 산출물 작성 |
| D5 | 기록 | `review/debates/` 토론 로그 + plan/draft 산출물 반영 |
| D6 | Codex 호출 | `codex:codex-rescue` 에이전트, **read-only**(의견 생성), 2라운드+는 `--resume` 멀티턴 |
| D7 | 폴백 | Codex 실패·미합의해도 워크플로 안 막힘 → **Claude 단독 진행으로 폴백** |

## 3. Architecture & Components

**오케스트레이션:** Claude(메인 루프)가 토론 오케스트레이터. 각 라운드에서 `codex:codex-rescue`를 read-only로 호출(프롬프트에 단계별 역할 + 현재까지 입장 포함), `--resume`으로 Codex 맥락 유지. 수렴 판정·로그·산출물 반영은 Claude가 담당.

**신규 파일**

| 파일 | 역할 |
|------|------|
| `docs/debate_protocol.md` | **단일 기준 문서.** 라운드 흐름·수렴 판정·단계별 Codex 역할·로그 형식·에러 처리 정의. 다른 문서는 참조만 |
| `.claude/commands/paper-debate.md` | `/paper-debate <주제>` slash command 진입점 |
| `review/debates/_TEMPLATE.debate.md` | 토론 로그 템플릿 |
| `review/debates/.gitkeep` | 디렉토리 유지 |

**수정 파일**

| 파일 | 변경 |
|------|------|
| `CLAUDE.md` | Quick Commands에 `/paper-debate` 추가; Phase 2·3·4·8 워크플로에 "작성 전 토론 제안" 지점 명시; File Roles·구조 트리에 신규 파일 등록 |
| `docs/statistical_analysis_guide.md`, `docs/draft_plan_template.md`, `docs/revision_guide.md` 등 | 해당 단계에 "이 단계는 `/paper-debate` 권장" 훅 한 줄 |

**설계 원칙:** 토론 로직은 전부 `debate_protocol.md` 한 곳에 모으고, command와 Phase 가이드는 참조만 한다(단일 기준). 기존 "docs 가이드 + 게이트 원장" 패턴과 일치.

## 4. Debate Protocol Flow

**라운드 흐름** (합의까지, 상한 3):

```
R0 준비   Claude가 주제에 대한 접근·골격(입장) + 근거 작성  (완성 산출물 아님)
R1        Codex 호출(역할 부여) → Codex 입장 + Claude 안 비판
          → Claude가 수렴 판정
             ├ 수렴   → 합의 확정
             └ 미수렴 → R2
R2        Claude 재반박/수정안 → Codex(--resume) 재응답 → 수렴 판정
R3        동일 (상한)
상한 후 미합의 → 차이점 표 + Claude 추천 → 사용자 결정
합의 확정 → 그 합의를 바탕으로 산출물(plan/draft/response) 작성 → 로그 저장
```

**수렴 판정** (매 라운드 끝, Claude 수행):
- **완전 합의** — 양측 같은 결론·근거 → 종료, 산출물 반영
- **부분 합의** — 핵심 합의 + 세부 차이 → 합의분 채택 + 차이 명시
- **미합의** — 핵심 입장 갈림 → 다음 라운드, 상한 시 사용자 에스컬레이션

**단계별 Codex 역할** (프롬프트에서 부여하는 동료 저자 관점):

| 단계 | Codex 역할 | 토론 초점 |
|------|-----------|-----------|
| Planning / 논문 계획 | 전략 담당 공동 저자 | 연구 질문의 약점, 더 나은 framing, novelty |
| 통계 계획 | 통계 담당 공동 저자 | 검정 선택 타당성, 가정 위반, 다중비교, 대안 |
| 논리 구조 / 문단 구조 | 논리 담당 공동 저자 | 논리 비약, 순서, 응집성, 중복 |
| Reviewer response | 공동 저자(co-author) | 코멘트별 최선의 대응 전략. 예상 reviewer 반박 점검 포함 |
| 일반 (수동 호출) | 균형 비평자 | 주제에 맞게 자동 설정 |

**프레임:** 토론은 대립이 아니라 두 co-author가 다른 각도에서 보강하는 협력이다. 건설적 반론은 하되 목표는 합의된 더 나은 결과물.

## 5. Activation & Workflow Integration

**수동 발동:** `/paper-debate <주제>` — 어느 단계든 호출. 단계 명시 시 그 역할로, 아니면 주제에서 자동 추론(균형 비평자).

**자동 제안 지점** (작성 **전**, 워크플로가 먼저 제안):

| Phase | 시점 (작성 전) | Codex 역할 |
|-------|----------------|-----------|
| 2 (Analysis) | 분석 접근 구상 → 합의 → `analysis_plan.md` 작성 | 통계 담당 공동 저자 |
| 3 (Draft Plan) | key message·구조 구상 → 합의 → `draft_plan.md` 작성 | 전략 담당 공동 저자 |
| 4 (Draft) | 핵심 섹션 논증 골격 구상 → 합의 → 섹션 작성 | 논리 담당 공동 저자 |
| 8 (Revision) | 대응 전략 구상 → 합의 → response letter 작성 | 공동 저자(co-author) |

**제안 규칙 (성가심 방지):**
- 제안은 **선택**: "이 단계는 토론이 도움됩니다. `/paper-debate` 할까요? (Codex 여러 번 호출, 비용 있음)" → 수락 시 진행, 거부 시 그대로.
- **단계당 1회만** 제안. 사용자가 "이번 논문은 토론 생략"이라 하면 이후 제안 안 함.
- 토론은 통과 필수 게이트가 **아님** — 기존 검증 게이트(constraint/citation/numbers/logic)와 별개.

## 6. Logging, Output Reflection & Error Handling

**로그 파일** `review/debates/YYYYMMDD_<topic>.debate.md`:
```
주제 / 단계 / Codex 역할 / 날짜 / 결과(합의·부분합의·미합의)
─ Claude 초기 입장
─ Codex 초기 입장
─ 라운드별 교환 (요약)
─ 최종 합의  (또는: 차이점 표 + Claude 추천)
─ 반영처: 합의가 들어간 plan/draft/response 파일
```

**산출물 반영:** 합의 확정 → 해당 `analysis_plan`/`draft_plan`/draft/response에 반영 → 로그에 반영처 기록(추적성).

**에러 처리**

| 상황 | 처리 |
|------|------|
| Codex 호출 실패(빈 출력) | 토론 중단 → **Claude 단독 진행 폴백** + 사용자 알림 |
| 상한 3라운드 미합의 | 차이점 표 + Claude 추천 → 사용자 결정 |
| Codex 응답 주제 이탈/무의미 | Claude 1회 재요청, 그래도 안 되면 폴백 |
| 사용자 도중 중단 | 현재까지 합의분만 반영 또는 폐기(사용자 선택) |

**안전장치:** 토론은 품질 보조이므로 Codex가 안 되거나 합의가 안 나도 **워크플로는 절대 막히지 않는다** — 항상 Claude 단독 폴백.

## 7. Related Sub-Project B: Adversarial Review (별도, 추후 설계)

paper-debate(협력)와 **반대 성격**의 독립 sub-project. A 완료 후 별도 spec → plan → 구현.

- **목적:** 완성된 답변/원고를 **적대적으로** 공격해 허점·약점을 발굴 (작성 **후**, 적대적 — A는 작성 전·협력).
- **백엔드 2종:**
  - codex `/codex:adversarial-review`를 논문용으로 응용
  - **OpenRouter API** (모델 다양성 — reviewer 페르소나 선택 폭이 큼)
- **실행 시 백엔드 선택**(codex / OpenRouter)을 사용자에게 물음. **멀티 선택 가능** — 여러 모델이 동시에 공격하여 서로 다른 blind spot 커버.
- 적용 후보: reviewer response 최종본, Discussion/limitation, 주요 주장 문단.

## 8. Summary of Files

**신규:** `docs/debate_protocol.md`, `.claude/commands/paper-debate.md`, `review/debates/_TEMPLATE.debate.md`, `review/debates/.gitkeep`
**수정:** `CLAUDE.md`, `docs/statistical_analysis_guide.md`, `docs/draft_plan_template.md`, `docs/revision_guide.md`

## 9. Open Questions (구현 plan에서 확정)

- `debate_protocol.md`의 정확한 프롬프트 템플릿(단계별 역할 문구) 초안.
- 자동 제안을 CLAUDE.md 규칙으로 둘지, 각 Phase 가이드에 분산할지의 정확한 배치.
- 로그 파일명 `<topic>` slug 규칙.
